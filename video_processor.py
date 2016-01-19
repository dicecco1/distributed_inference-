import cv2
`
cap = cv2.VideoCapture('Wildlife.wmv')

count = 1

if cap.isOpened():
    rval, frame = cap.read()
else:
    rval = False

while rval:
    rval, frame = cap.read()
    if count % 20 == 0:
        cv2.imwrite(str(count) + '.jpg', frame)
    count = count + 1
    cv2.waitKey(1)
cap.release()

#while cap.isOpened():
#    ret, frame = cap.read()
#    if count % 50 == 0:
#        cv2.imwrite("frame%d.jpg" % count, frame)
#        count = count + 1

#cap.release()
#cap.destroyAllWindows()
