#!/bin/zsh
cd ~/CV_Tool || exit 1
~/CV_Tool/cv_env/bin/python3 - <<'EOF' > archive/dump.txt 2>&1
import butler, inspect
for f in ('_service_act','_case_sweep','_event_tick','_tick_loop','_tick_log','extract_text_ocr','_name_from_first_line','heuristic_name','_canonical_person_name','_display_name','_fast_rename','rename_diag','_eyename_of','_stem_norm','_convert_to_pdf','_pages_pdf','_jd_like_name','_portal_name','_rename_ledger','_repath_ledgers','_lock_root','desk_load','seat_rename_check'):
    o = getattr(butler, f, None)
    o = getattr(o, '__wrapped__', o)  # DUMP-UNWRAP-TRUE v85.139
    print('==== %s ====' % f); print(inspect.getsource(o) if o else 'MISSING')  # DUMP-UNWRAP-TRUE v85.139
src = open(butler.__file__).read().split('\n')
k = next(i for i,l in enumerate(src) if 'SERVICE-QUEUE v85.58' in l)
print('==== drain region ===='); print('\n'.join(src[k-3:k+22]))
print('==== module constants ====')
for i,l in enumerate(src):
    if l.startswith('OCRBIN') or l.startswith('OCR_SEM') or l.startswith('extract_text =') or l.startswith('BASE_DIR'):
        print(i+1, l)
EOF
