def detect(xmin,ymin,xmax,ymax,frame):
    # 요소1[pct]
    bbox = (xmax-xmin)*(ymax-ymin)
    pct = round(100 * bbox / (frame.shape[0]*frame.shape[1]))
    # 요소2[loc]
    localdic={0:"왼쪽 위", 1:'위', 2:'오른쪽 위', 3:"왼쪽", 4:"가운데", 5:"오른쪽", 6:"왼쪽 아래", 7:"아래", 8:"오른쪽 아래"}
    x_center = (xmin+xmax)/2
    y_center = (ymin+ymax)/2
    loc = localdic[int(x_center/frame.shape[1]*3)+3*int(y_center/frame.shape[0]*3)]
    return pct,loc

def box_to_pct(boxes, width, height):
    pct = []
    for box in boxes:
        xmin, ymin, xmax, ymax = map(int, box)
        pct.append((xmax-xmin)*(ymax-ymin)/(width*height)*100)
    return pct

import cv2
import numpy as np

def head_Pose(image, face_mesh):
    global text
    global say
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = face_mesh.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    img_h, img_w = image.shape[0], image.shape[1]
    face_3d = []
    face_2d = []

    text = "No face detected"
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    # Get the 2D Coordinates
                    face_2d.append([x, y])
                    # Get the 3D Coordinates
                    face_3d.append([x, y, lm.z])       
            
            # Convert it to the NumPy array
            face_2d = np.array(face_2d, dtype=np.float64)

            # Convert it to the NumPy array
            face_3d = np.array(face_3d, dtype=np.float64)

            # The camera matrix
            focal_length = 1 * img_w

            cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                    [0, focal_length, img_w / 2],
                                    [0, 0, 1]])

            # The distortion parameters
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            # Solve PnP
            suc, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

            # Get rotational matrix
            rmat = cv2.Rodrigues(rot_vec)[0]

            # Get angles
            angles = cv2.RQDecomp3x3(rmat)[0]

            # Get the rotation degree
            x = angles[0] * 360
            y = angles[1] * 360

            # See where the user's head tilting
            if y < -5:
                text_1 = f"looking left {round(y,1)}"
                say_1 = f"왼쪽 응시중입니다."
            elif y > 5:
                text_1 = f"looking right {round(y,1)}"
                say_1 = f"오른쪽 응시중입니다."
            else:
                text_1 = "looking forward"
                say_1 = "정면 응시중입니다."

            if x < -3.5:
                text_2 = f"looking down {round(x,1)}"
                say_2 = f"아래쪽 응시중입니다."
            elif x > 4:
                text_2 = f"looking up {round(x,1)}"
                say_2 = f"위쪽 응시중입니다."
            else:
                text_2 = ""
                say_2 = ""

            text = text_1 + " " + text_2
            say = say_1 + " " + say_2
    return text, say

