import bleach
#print(bleach.ALLOWED_ATTRIBUTES)

def filter_src(name, value):
    if name in ('alt', 'height', 'width', 'src'):
        return True
    if name == 'src':
    .         p = urlparse(value)
            ...         return (not p.netloc) or p.netloc == 'mydomain.com'
            ...     return False

BLEACH_ATTR = bleach.ALLOWED_ATTRIBUTES.copy()
BLEACH_ATTR['img'] = ['src']

def filter(data):
    return bleach.clean(
       data,
       tags=bleach.ALLOWED_TAGS+['img','br','p'],
       attributes=BLEACH_ATTR))
       

with open('bleach_test_data.html', 'r') as myfile:
    data=myfile.read()
    
    print(bleach.clean(
       data,
       tags=bleach.ALLOWED_TAGS+['img','br','p'],
       attributes=BLEACH_ATTR))
       