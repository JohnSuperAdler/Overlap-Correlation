import numpy as np

def ReLU(x):
    return x * (x > 0)

class OverlapCorr:
    
    def __init__(self, mx_1, mx_2, position_1, position_2):
        self.mx_1 = mx_1
        self.mx_2 = mx_2
        self.position_1 = np.array(position_1)
        self.position_2 = np.array(position_2)
        # position_diff : Distance from position_1 to position_2
        self.position_diff = np.array([p2-p1 for p1, p2 in zip(self.position_1, self.position_2)])
        # Get side length of matrices
        self.shape_mx_1 = np.array(np.shape(self.mx_1))
        self.shape_mx_2 = np.array(np.shape(self.mx_2))
        # Get slice interval of overlap area
        from_1 = ReLU(  self.position_diff) - ReLU(  self.position_diff - self.shape_mx_1)
        from_2 = ReLU(- self.position_diff) - ReLU(- self.position_diff - self.shape_mx_2)
        to_1   = ReLU(self.shape_mx_1                      - ReLU(self.shape_mx_1 - self.shape_mx_2 - self.position_diff))
        to_2   = ReLU(self.shape_mx_1 - self.position_diff - ReLU(self.shape_mx_1 - self.shape_mx_2 - self.position_diff))
        # Slice input matrices
        self.overlap_mx_1 = self.mx_1[tuple([slice(x,y) for x, y in zip(from_1, to_1)])]
        self.overlap_mx_2 = self.mx_2[tuple([slice(x,y) for x, y in zip(from_2, to_2)])]
        self.shape_overlap_mx_1 = np.array(np.shape(self.overlap_mx_1))
        self.shape_overlap_mx_2 = np.array(np.shape(self.overlap_mx_2))
        
    # Original dimension correlation
    def OverlapCC(self, ifnan=np.nan):
        overlap_mx_1_1d = self.overlap_mx_1.reshape(-1)
        overlap_mx_2_1d = self.overlap_mx_2.reshape(-1)
        PC = np.corrcoef(overlap_mx_1_1d, overlap_mx_2_1d)[0][1]
        if np.isnan(PC):
            PC = ifnan
        return PC
    
    # MIP (maximum intensity projection) correlation
    def OverlapMIPCC(self, ifnan=np.nan, merge=True):
        PC_ar = np.full((self.overlap_mx_1.ndim), np.nan)
        for dim in range(self.overlap_mx_1.ndim):
            overlap_mx_1_1d = np.amax(self.overlap_mx_1, axis=dim).reshape(-1)
            overlap_mx_2_1d = np.amax(self.overlap_mx_2, axis=dim).reshape(-1)
            temp_PC = np.corrcoef(overlap_mx_1_1d, overlap_mx_2_1d)[0][1]
            if np.isnan(temp_PC):
                temp_PC = ifnan
            PC_ar[dim] = temp_PC
        if merge:
            PC = np.nanmean(PC_ar)
            return PC
        else:
            return PC_ar
