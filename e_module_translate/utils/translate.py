import re
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
import html
from googletrans import Translator
import polib

PLACEHOLDER_REGEX = re.compile(r'({[^}]+}|%[sdf]|%\(\w+\)[sdf]|%\d+\$[sdf]|\[[^\]]+\])')
HTML_TAG_REGEX = re.compile(r'<[^>]+>')
MARKER_REGEX = re.compile(r'__(s|e)(\d+)__')

def extract_placeholders(text):
    placeholders = []
    def replace_match(match):
        ph = match.group(0)
        if ph not in placeholders:
            placeholders.append(ph)
        idx = placeholders.index(ph)
        return f"__{idx}__"
    clean_text = PLACEHOLDER_REGEX.sub(replace_match, text)
    return clean_text, placeholders

def restore_placeholders(text, placeholders):
    for i, ph in enumerate(placeholders):
        text = text.replace(f"__{i}__", ph)
    return text

def has_html(text):
    return bool(HTML_TAG_REGEX.search(text))

def prepare_html(text):
    if not has_html(text):
        return text, {}
    soup = BeautifulSoup(f"<root>{text}</root>", 'html.parser')
    tag_map = {}
    tag_counter = 0
    
    def process_node(node):
        nonlocal tag_counter
        if isinstance(node, str):
            return str(node)
        current_id = tag_counter
        tag_counter += 1
        attrs = {}
        if node.attrs:
            for k, v in node.attrs.items():
                attrs[k] = ' '.join(v) if isinstance(v, list) else str(v)
        tag_map[current_id] = {'name': node.name, 'attrs': attrs}
        inner = ''.join(process_node(child) for child in node.contents)
        return f" __s{current_id}__ {inner} __e{current_id}__ "
    
    result = ''.join(process_node(child) for child in soup.root.contents)
    return result.strip(), tag_map

def restore_html(text, tag_map):
    if not tag_map:
        return text
    
    def replace_marker(match):
        marker_type, tag_id = match.groups()
        tag_id = int(tag_id)
        if tag_id not in tag_map:
            return match.group(0)
        tag_data = tag_map[tag_id]
        tag_name = tag_data['name']
        if marker_type == 's':
            if tag_data.get('attrs'):
                attrs_str = ' '.join(f'{k}="{html.escape(v)}"' for k, v in tag_data['attrs'].items())
                return f"<{tag_name} {attrs_str}>"
            return f"<{tag_name}>"
        else:
            return f"</{tag_name}>"
    
    text = MARKER_REGEX.sub(replace_marker, text)
    text = re.sub(r'>\s+<', '><', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

async def translate_batch(texts, dest_lang, max_retries=3):
    if not texts:
        return []
    translator = Translator()
    for attempt in range(max_retries):
        try:
            results = await translator.translate(texts, dest=dest_lang)
            return [r.text if r else "" for r in results]
        except:
            if attempt == max_retries - 1:
                return texts
            await asyncio.sleep((attempt + 1) * 2)
    return texts

async def translate_entries(texts, dest_lang, batch_size, delay):
    if not texts:
        return []
    total = len(texts)
    results = []
    for i in range(0, total, batch_size):
        batch = texts[i:i + batch_size]
        translated = await translate_batch(batch, dest_lang)
        results.extend(translated)
        if i + batch_size < total:
            await asyncio.sleep(delay)
    return results

def translate_values(values:list, lang_code, batch_size=40, delay=0.5):
    if not values:
        return []
    
    prepared = []
    clean_texts = []
    
    for original in values:
        clean_text, placeholders = extract_placeholders(original)
        clean_text, html_map = prepare_html(clean_text)
        prepared.append({
            'placeholders': placeholders,
            'html_map': html_map
        })
        clean_texts.append(clean_text)
    
    async def do_translate():
        return await translate_entries(clean_texts, lang_code, batch_size, delay)
    
    try:
        translated_texts = asyncio.run(do_translate())
    except:
        return []
    
    result = []
    for prep, translated in zip(prepared, translated_texts):
        text = restore_html(translated, prep['html_map'])
        text = restore_placeholders(text, prep['placeholders'])
        result.append(text)
    
    return result

def generate_po_metadata(lang_code, pot_metadata=None):
    plural_forms = {
        'es': 'nplurals=2; plural=(n != 1);',
        'en': 'nplurals=2; plural=(n != 1);',
        'pt': 'nplurals=2; plural=(n != 1);',
        'fr': 'nplurals=2; plural=(n > 1);',
        'de': 'nplurals=2; plural=(n != 1);',
    }
    lang = lang_code.split('_')[0].lower()
    now = datetime.now().strftime('%Y-%m-%d %H:%M%z')
    
    metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': '',
        'POT-Creation-Date': now,
        'PO-Revision-Date': now,
        'Last-Translator': 'PoTranslator <acevedoesteban999@gmail.com>',
        'Language-Team': 'PoTranslator <acevedoesteban999@gmail.com>',
        'Language': lang_code,
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=UTF-8',
        'Content-Transfer-Encoding': '8bit',
        'X-Generator': 'PoTranslator',
        'Plural-Forms': plural_forms.get(lang, 'nplurals=2; plural=(n != 1);'),
    }
    
    if pot_metadata:
        for key in ['Project-Id-Version', 'Report-Msgid-Bugs-To', 'POT-Creation-Date']:
            if key in pot_metadata:
                metadata[key] = pot_metadata[key]
    
    return metadata

def generate_po_content(pot_data, translations, lang_code, pot_metadata=None):
    po = polib.POFile(wrapwidth=78)
    po.metadata = generate_po_metadata(lang_code, pot_metadata)
    for key, msgid in pot_data.items():
        entry = polib.POEntry(msgid=msgid, msgstr=translations.get(key, ''))
        po.append(entry)
    return str(po)