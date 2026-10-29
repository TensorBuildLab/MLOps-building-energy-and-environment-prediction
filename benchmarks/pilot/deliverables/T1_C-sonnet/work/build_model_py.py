src = open('feats.py', encoding='utf-8').read()
part = open('work/predict_part.py', encoding='utf-8').read()
open('model.py', 'w', encoding='utf-8').write(src.rstrip() + '\n' + part)
print('model.py written')
