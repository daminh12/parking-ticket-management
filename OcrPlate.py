from ultralytics import YOLO
import cv2
import numpy as np

class OcrPlate:
    # Để mục khởi tạo này riêng với set_data vì load model quá nặng
    def __init__(self, path_model_detect_plate, path_model_ocr):
        self.model_license = YOLO(path_model_detect_plate)
        self.model_ocr = YOLO(path_model_ocr)

    # Đặt data đầu vào chính là ảnh cần dự đoán
    def set_data(self, imgage_input):
        self.image_input = imgage_input.copy() # Tránh việc bị thay đổi đầu vào
        self.image_output = imgage_input # Ảnh đầu ra sau khi vẽ các bounding box và các nhãn của từng biển
        self.digit_out = 'unknow' # Kí tự của biển cuối cùng được giải mã
        self.box_xyxy = None # Chứa các thông số tọa độ của bouding boxes (tensor 2D)
        self.detect_plate_ocr() # Chạy luôn hàm để detect luôn

    def detect_plate_ocr(self):
        """Hàm này sẽ thiết đặt digit_out là kí tự trên biển số đã được sắp xếp hoàn chỉnh
và thiết đặt image_out là ảnh được vẽ (box và kí tự lên trên box)"""
        # dictinary các label được mã hóa
        lbs = self.model_ocr.names
        res_detect_plate = self.model_license.predict(source= self.image_input, conf = 0.8, verbose = False)

        # Lấy thông tin ((x, y) cạnh trên cùng bên trái và (x, y) cạnh dưới cùng bên phải) của các bounding box
        # và gán vào thuộc tính box_xyxy
        box = res_detect_plate[0].boxes.xyxy
        self.box_xyxy = box

        # Duyệt từng 'box'
        for x, y, x1, y1 in box:
            # openCv yêu cầu các tọa độ điểm cần phải là số nguyên
            x, y, x1, y1 = map(int, [x, y, x1, y1])
            # Cắt ảnh biển số ra trước rồi mới vẽ
            img_plate = self.image_input[y : y1, x : x1]
            # predict các kí tự của biển số
            res_ocr = self.model_ocr.predict(verbose = False, source= img_plate, conf = 0.2)
            # Lấy số lượng kí tự của biển số vừa predict
            len_digits = len(res_ocr[0].boxes.cls) # == len(box)

            # Đặt digit là unknow trước
            digit = 'unknow'
            # Biển số Việt Nam thường có 7 đến 10 kí tự
            # Và ta cũng chỉ chấp nhận độ tin cậy của dự đoán các kí tự này nhỏ nhất của nó là phải lớn hơn 0.7
            if (len_digits >= 7 and len_digits <= 10) and min(res_ocr[0].boxes.conf) > 0.7:
                # Đoạn code dưới là tạo ra 1 mảng np.array 2D mà các cột lần lượt là x_center, y_center, label đã được mã hóa
                cls = res_ocr[0].boxes.cls # cls là labels các kí tự nhưng đã được mã hóa
                cls = cls.reshape(-1, 1) # Reshape về dạng 1 cột
                cls = np.array(cls) # Chuyển từ tensor sang numpy để tiện tính toán

                # Lấy ra x, y của center bounding box
                xy_center = res_ocr[0].boxes.xywh[:, :2] # lấy tất cả các dòng của 2 cột đầu (chính là center của box)
                xy_center = np.array(xy_center)

                # Ghép mảng 2D theo chiều ngang với nhau hoziron, có thể dùng concatenate theo trục axis = 1
                data = np.hstack([xy_center, cls])
                # Gọi hàm trả về kí tự của biển số (đã được sắp xếp lại) và gán lại vào biến digit
                digit = self.process_ocr(data_center_labe= data, labels_encoder= lbs)
                # Chạy hết các box thì digit out này chính là nhãn đã được giải mã của cái biển cuối cùng
                self.digit_out = digit

                # Vẽ lên màn box và biển
            cv2.putText(self.image_output, str(digit), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            cv2.rectangle(self.image_output, (x, y), (x1, y1), (0, 255, 0), 2)
    