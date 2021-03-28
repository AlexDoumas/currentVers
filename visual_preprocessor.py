###
### visual_preprocessor.py
### Contour extraction: loads images from the folder, extract only 'outside' contours and key information such as extreme points, area, centroid, height, width, etc.
### Conversion of contour data into DORA format.
### Same_shape relation:
# * each contour is divided into three subcontours; three triangles are inscribed into each subcontour, connecting 1st, last and local extreme points;
# * three angles in each triangle are converted into a unique value, ticker, characterising 'magnitude' of a triangle (using binomial coefficients)
# an instance of the class Shape holds all the processed info about the contour
###
import copy, cv2, math, numpy, os, random, re, scipy.special
from dataclasses import dataclass
import compute_tickers

@dataclass
class Shape():
    name: str
    contour: numpy.array
    topmost: tuple
    rightmost: tuple
    bottommost: tuple
    leftmost: tuple
    area: float
    height: int
    width: int
    triangles: list
    tickers: list
    sym_props: list

    def print_shape(self):
        print('Shape: ' + str(self))

@dataclass
class Triangle():
    # vertices
    A: tuple
    B: tuple
    C: tuple
    # angles
    a: float = 0
    b: float = 0
    c: float = 0

    # returns the squared length of an edge
    def sq_length(self, X, Y):
        # print(X, Y)
        xDiff = X[0] - Y[0]
        yDiff = X[1] - Y[1]
        return xDiff * xDiff + yDiff * yDiff

    def get_angles(self):
    	# squared lengths
    	AB2 = self.sq_length(self.A, self.B)
    	AC2 = self.sq_length(self.A, self.C)
    	BC2 = self.sq_length(self.B, self.C)

    	# side lengths
    	AB = math.sqrt(AB2)
    	AC = math.sqrt(AC2)
    	BC = math.sqrt(BC2)

    	# cosine law
    	a = math.acos((BC2 + AB2 - AC2) / (2 * BC * AB))
    	b = math.acos((AC2 + AB2 - BC2) / (2 * AC * AB))
    	c = math.acos((AC2 + BC2 - AB2) / (2 * AC * BC))

    	# convert to degrees
    	self.a = a * 180 / math.pi
    	self.b = b * 180 / math.pi
    	self.c = c * 180 / math.pi

@ dataclass
class Ticker():
    x: int = 0
    y: int = 0
    z: int = 0
    ticker_value: int = 0

    # uses formula with binomial coefficients to convert three values of angles into a unique number, 'ticker'
    def compute_tricker(self):
        self.ticker_value = round(scipy.special.binom(self.x, 1) + scipy.special.binom(self.x + self.y + self.z, 2) + scipy.special.binom(self.x + self.y + self.z + 2, 3))

    def print_ticker(self):
        print(self)

class Processor:
    def __init__(self, stimulus_count = 20, folder = 'problem_1_images', filename = 'fea_1_', x_max = 640, y_max = 640, display_shapes = False):
        self.stimulus_count = stimulus_count # how many shapes to process
        self.folder = folder # where the images are
        self.filename = filename # the file's name template (all images are .png)
        self.display_shapes = display_shapes # do we want the visual
        self.x_max = x_max # length of the window to display contours
        self.y_max = y_max # width of the window to display contours
        self.font = cv2.FONT_HERSHEY_COMPLEX # font for openCV text
        self.sym_props = [] # all the shapes in DORA format

    def inscribe_triangles(self, contour):
        tickers, triangles = [], []
        # the current contour we are working wuth
        cnt = contour

        # divide a contour into 3 subcontours
        num_of_subs = 3
        sub1, sub2, sub3 = numpy.array_split(cnt, num_of_subs)

        # tickers for each subcontour
        sub_tickers = []
        # find the 1st and the last points of the subcontour
        for sub in [sub1, sub2, sub3]:
            # find the point in the subcontour that is furthest from the line between the 1st and the last points
            x1, y1 = sub[0][0][0], sub[0][0][1]
            x2, y2 = sub[-1][0][0], sub[-1][0][1]

            far_pnt = None
            max_dist = 0
            for pnt in sub:
                # print(pnt)
                x0, y0 = pnt[0][0], pnt[0][1]
                # formula of a distance between a point (x0, y0) and a line through (x1, y1) and (x2, y2)
                dist = abs((x2-x1)*(y1-y0) - (x1-x0)*(y2-y1)) / numpy.sqrt(numpy.square(x2-x1) + numpy.square(y2-y1))
                # find the local extremum
                if dist > max_dist:
                    max_dist = dist
                    # the most distant point from the subcontour line (from 1st to last points)
                    far_pnt = (x0, y0)

            fst_pnt, lst_pnt = (x1, y1), (x2, y2)

            # triangle vertices
            A = fst_pnt
            B = lst_pnt
            C = far_pnt
            triangles.append([A, B, C])

            # make a triangle, get its angles
            tr = Triangle(A, B, C)
            tr.get_angles()

            # compute a ticker
            ti = Ticker(int(tr.a), int(tr.b), int(tr.c))
            ti.compute_tricker()
            tickers.append(int(ti.ticker_value))

        return triangles, tickers

    # object in DORA format
    def gen_obj_semantics(self, cShape):
        obj_sem_list = []
        dim_dict = {'y_topmost': cShape.topmost[1], 'x_rightmost': cShape.rightmost[0], 'y_bottommost': cShape.bottommost[1], 'x_leftmost': cShape.leftmost[0],
                    'area': cShape.area, 'height': cShape.height, 'width': cShape.width,
                    'tOne': cShape.tickers[0], 'tTwo': cShape.tickers[1], 'tThree': cShape.tickers[2]}

        # each characteristic of a cell is a separate featural dimension with a value
        for key, value in dim_dict.items():
            obj_sem_list.append([key, 1, key, 'nil', 'state'])
            obj_sem_list.append([key + str(value), 1, key, value, 'value'])

        return obj_sem_list

    # generate DORA's input format for the current stimulus
    def to_DORA(self, cShape, curr_index, pic_name):
        curr_prop, sym_props = [], []

        # DORA's input structure
        cDict = {'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [],
        'higher_order': False, 'object_name': '', 'object_sem': [], 'P': 'nil'}],
        'set': '', 'category': None, 'analog': None}

        obj_sem_list = self.gen_obj_semantics(cShape)

        # semantic features and a name of an exemplar
        for nDict in cDict['RBs']:
            nDict['object_name'] = cShape.name
            nDict['object_sem'] = obj_sem_list

        # set and the analog number
        cDict['set'] = 'driver'
        cDict['analog'] = curr_index

        # correct category
        image_num = re.findall('[0-9]+', str(pic_name)) # extract the number of the image; returns the list with 0) number of the problem, 1) number of the image
        if int(image_num[1]) < 10:
            cDict['category'] = 'A'
        else:
            cDict['category'] = 'B'

        curr_prop.append(cDict)

        # making sure sym_props is the list of dictionaries, not the *list of lists* of dictionaries
        for mDict in curr_prop:
            sym_props.append(mDict) # shape's symProps
            self.sym_props.append(mDict) # farm's symProps

        return sym_props

    # draw countours
    def get_visual(self, shapes, index):
        img = numpy.zeros((self.x_max, self.y_max, 3), dtype = "uint8")
        img[:] = (255)

        for sh in shapes:
            cv2.drawContours(img, [sh.contour], 0, (127), 2)

        cv2.imshow('Shapes', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # list of images to preprocess in the folder
    def process_images(self):
        image_list = []
        for i in range(self.stimulus_count):
            img_name = os.path.join(self.folder, self.filename + str(i) + '.png')
            image_list.append(img_name)
        random.shuffle(image_list)
        return image_list

    # extract contours from the image and all the key information about them
    def process_contours(self, image_list):
        analog_counter = 0 # stimulus counter
        for pic in image_list:
            # print(pic)
            img = cv2.imread(pic, cv2.IMREAD_GRAYSCALE)
            _, threshold = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
            # USE RETR_CCOMP; hierarchy is the array with a row per contour, four numbers in the row -- 0. next contour, 1. prev., 2. first child, 3. parent
            contours, hierarchy = cv2.findContours(threshold, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

            i = 0 # contour counter in an image
            # collect only essential contours and sort them by their area, smallest first
            ordered_contours = []
            for cnt in contours:
                # we only need outside contours, not inside ones or an image frame, thus, those contours wihtout parents in the RETR_CCOMP hierarchy get dropped
                if hierarchy[0][i][3] == -1:
                    pass
                else:
                    # approximation of a contour shape to another shape with less number of vertices depending upon the specified precision
                    # an implementation of Douglas-Peucker algorithm
                    approx = cv2.approxPolyDP(cnt, 0.001*cv2.arcLength(cnt, True), True)
                    # area of the contour
                    area = int(cv2.contourArea(approx))
                    ordered_contours.append([approx, area])
                i += 1
            # sort contours by area
            ordered_contours = sorted(ordered_contours, key=lambda x: x[1])

            obj_count = 1 # object counter -- how many objects (contours to process) in an image
            shapes = []
            for pair in ordered_contours:
                approx = pair[0]

                # extreme points
                topmost = tuple(approx[approx[:,:,1].argmin()][0])
                rightmost = tuple(approx[approx[:,:,0].argmax()][0])
                bottommost = tuple(approx[approx[:,:,1].argmax()][0])
                leftmost = tuple(approx[approx[:,:,0].argmin()][0])

                # area of the contour
                area = int(cv2.contourArea(approx))

                # height = y_bottommost - y_topmost
                height = bottommost[1] - topmost[1]
                # width = x_rightmost - x_leftmost
                width = rightmost[0] - leftmost[0]

                # extract the number of the image; returns the list with 0) number of the folder, 1) number of the problem, 2) number of the image
                num = re.findall('[0-9]+', pic)
                name = self.filename + str(num[2])
                # an instance of the class Shape to hold all the contour info
                sh = Shape(name + '_' + str(analog_counter+1) + str(obj_count), approx, topmost, rightmost, bottommost, leftmost, area, height, width, [], [], [])
                # inscribe the triangles and get their tickers
                sh.triangles, sh.tickers = self.inscribe_triangles(approx)
                # convert Shape's data into DORA format
                sh.sym_props = self.to_DORA(sh, analog_counter, name)

                shapes.append(sh)
                obj_count += 1
            analog_counter += 1
            # draw shapes
            if self.display_shapes:
                self.get_visual(shapes, obj_count-1)

            # clean memory
            for sh in shapes:
                del sh

    def run_processor(self):
        images = self.process_images()
        self.process_contours(images)
        f = open('sym_file_test.py', "w")
        f.write('simType = \'sym_file\' \nsymProps = ' + str(self.sym_props))
        f.close()
        print('\nNew sym_file is generated.\n')

### MAIN PROGRAM
pr = Processor(folder = 'problem_1_images', filename = 'fea_1_')
pr.run_processor()
