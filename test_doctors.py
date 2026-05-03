import sys
sys.path.insert(0, '.')
from streamlit_app import get_suitable_doctors

print('Testing doctor filtering...')
try:
    # Test 1: Cardiac diagnosis
    doctors = get_suitable_doctors('Patient has severe cardiac arrhythmia and heart disease')
    print('Test 1 (Cardiac): Found {} doctors'.format(len(doctors)))
    if doctors:
        print('   Sample: {}'.format(doctors[0]))
    
    # Test 2: Skin diagnosis
    doctors2 = get_suitable_doctors('Severe skin rash and dermatitis on face')
    print('Test 2 (Skin): Found {} doctors'.format(len(doctors2)))
    if doctors2:
        print('   Sample: {}'.format(doctors2[0]))
    
    # Test 3: Create options like in the app
    options = ['{} ({}) - {}'.format(d.get('Doctor Name', 'Unknown'), d.get('Specialty', 'Unknown'), d.get('City', 'Unknown')) for d in doctors]
    print('Test 3 (Options): Created {} options'.format(len(options)))
    if options:
        print('   Sample option: {}'.format(options[0]))
    
    print('All tests passed!')
except Exception as e:
    print('Error: {}'.format(e))
    import traceback
    traceback.print_exc()
