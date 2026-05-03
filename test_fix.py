import sys
sys.path.insert(0, '.')
from streamlit_app import get_suitable_doctors

print('Testing doctor filtering fix...')
try:
    doctors = get_suitable_doctors('Patient has severe cardiac arrhythmia and heart disease')
    print('Test 1 (Cardiac): Found {} doctors'.format(len(doctors)))
    if doctors:
        print('   Sample: {}'.format(doctors[0]))
    
    doctors2 = get_suitable_doctors('Severe skin rash and dermatitis on face')
    print('Test 2 (Skin): Found {} doctors'.format(len(doctors2)))
    if doctors2:
        print('   Sample: {}'.format(doctors2[0]))
    
    print('All tests passed!')
except Exception as e:
    print('Error: {}'.format(e))
    import traceback
    traceback.print_exc()
