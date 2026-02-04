-- activate neutralization watermarks
UPDATE ir_ui_view
   SET active = true
 WHERE key = 'e_neutralize_ribbon.view_neutralize_pos_ribbon';
