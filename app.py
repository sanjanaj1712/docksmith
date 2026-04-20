import os
print('MY_VAR =', os.getenv('MY_VAR', 'not set'))
with open('/secret_inside_container.txt', 'w') as f:
    f.write('secret')
print('wrote secret inside container')
