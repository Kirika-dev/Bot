import cv2
import numpy as np
import mss

# Глобальные переменные для хранения координат области
ref_point = []
cropping = False

def click_and_crop(event, x, y, flags, param):
    global ref_point, cropping

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        cropping = True

    elif event == cv2.EVENT_LBUTTONUP:
        ref_point.append((x, y))
        cropping = False

        cv2.rectangle(param['img'], ref_point[0], ref_point[1], (0, 255, 0), 2)
        cv2.imshow("Выделите область", param['img'])

def main():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # основной монитор
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    clone = img.copy()
    cv2.namedWindow("Выделите область")
    cv2.setMouseCallback("Выделите область", click_and_crop, param={'img': img})

    print("Выделите область мышью и отпустите кнопку.")
    while True:
        cv2.imshow("Выделите область", img)
        key = cv2.waitKey(1) & 0xFF

        # При нажатии клавиши 'r' можно сбросить выбор
        if key == ord("r"):
            img = clone.copy()
            ref_point.clear()
            print("Выбор сброшен")

        # При нажатии клавиши 'q' выход из программы
        elif key == ord("q"):
            break

        # Если область выделена, выводим координаты и завершаем
        if len(ref_point) == 2:
            x1, y1 = ref_point[0]
            x2, y2 = ref_point[1]
            top = min(y1, y2)
            left = min(x1, x2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            print(f"Выделена область: top={top}, left={left}, width={width}, height={height}")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
