import requests

image_files = [
    'CG1.jpg', 'CG2-1.jpg', 'CG2-2.jpg', 'CG2-3.jpg', 'CG3-1.jpg', 'CG3-2.jpg', 'CG3-3.jpg', 'CG4-1.jpg', 
    'CG4-3.jpg', 'CG4-4-1.jpg', 'CG4-4-2.jpg', 'CG4-5.jpg', 'CG4-6.jpg', 'CG5-1.jpg', 'CG6-1.jpg', 'CG7-1.jpg', 
    'CG7-2.jpg', 'CG8-1-2.jpg', 'CG8-1-3.jpg', 'CG8-2.jpg', 'CG9-1.jpg', 'CG10-1.jpg', 'CG10-2.jpg', 'CG11-2.jpg', 
    'CG12-1.jpg', 'CG12-2.jpg', 'CG12-3.jpg', 'CG12-4.jpg', 'CG12-5.jpg', 'CG13-2.jpg', 'CG13-3.jpg', 'CG13-4.jpg', 
    'CG13-5.jpg', 'CG13-1.jpg', 'CG13-6.jpg', 'CG14-1.jpg', 'CG14-2.jpg', 'CG15-1.jpg', 'CG16-1-2.jpg', 'CG16-2-2.jpg', 
    'CG16-3.jpg', 'CG16-4.jpg', 'CG17-1.jpg', 'CG17-2.jpg', 'CG17-3.jpg', 'CG-18-0.jpg', 'CG-18-1.jpg', 'CG-18-2.jpg', 
    'CG19-1.jpg', 'CG19-2.jpg', 'CG20-1.jpg', 'CG20-2.jpg', 'CG21-1.jpg', 'CG22-1.jpg', 'CG22-2.jpg', 'CG22-3.jpg', 
    'CG23-1.jpg', 'CG24-1.jpg', 'CG25-1.jpg', 'CG25-2.jpg', 'CG25-3.jpg', 'CG26-1.jpg', 'CG26-2.jpg', 'CG27-1.jpg', 
    'CG27-2.jpg', 'CG27-3.jpg', 'CG28-1.jpg', 'CG28-2.jpg', 'CG28-3.jpg', 'CG29-3.jpg', 'CG29-4.jpg', 'CG29-7.jpg', 
    'CG30-1.jpg', 'CG30-2.jpg', 'CG30-3.jpg', 'CG30-4.jpg', 'CG30-5.jpg', 'CG30-6.jpg', 'CG30-7.jpg', 'CG30-8.jpg', 
    'CG30-9-1.jpg', 'CG30-9-2.jpg', 'CG31-1.jpg', 'CG31-2.jpg'
]

for i in image_files:
   with open(i, 'wb') as f:
      f.write(requests.get(f'https://act-webstatic.mihoyo.com/event_bh3_com/avg-anti-entropy/static_CN/baseDurandal/resources/cg/{i}').content)
      f.close()
