import numpy as np

element_stiffness_matrix_4node_p1_data= [
    {   
        "extent": (0, 2, 0, 2),
        "h": (1.0, 1.0),
        "origin": (0, 0),
        
        # 6 7-------4 6
        #  |         |
        #  |         |
        #  |         |
        # 0 1-------2 3
        "wiseclose_node": np.array([
            [0.49450549, 0.17857143, -0.3021978, -0.01373626, -0.24725275, -0.17857143, 0.05494505, 0.01373626],
            [0.17857143, 0.49450549, 0.01373626, 0.05494505, -0.17857143, -0.24725275, -0.01373626, -0.3021978],
            [-0.3021978, 0.01373626, 0.49450549, -0.17857143, 0.05494505, -0.01373626, -0.24725275, 0.17857143],
            [-0.01373626, 0.05494505, -0.17857143, 0.49450549, 0.01373626, -0.3021978, 0.17857143, -0.24725275],
            [-0.24725275, -0.17857143, 0.05494505, 0.01373626, 0.49450549, 0.17857143, -0.3021978, -0.01373626],
            [-0.17857143, -0.24725275, -0.01373626, -0.3021978, 0.17857143, 0.49450549, 0.01373626, 0.05494505],
            [0.05494505, -0.01373626, -0.24725275, 0.17857143, -0.3021978, 0.01373626, 0.49450549, -0.17857143],
            [0.01373626, -0.3021978, 0.17857143, -0.24725275, -0.01373626, 0.05494505, -0.17857143, 0.49450549]
        ], dtype=np.float64),

        # 2 3-------6 7
        #  |         |
        #  |         |
        #  |         |
        # 0 1-------4 5
        "yx_node": np.array([
            [0.49450549, 0.17857143, 0.05494505, 0.01373626, -0.3021978, -0.01373626, -0.24725275, -0.17857143],
            [0.17857143, 0.49450549, -0.01373626, -0.3021978, 0.01373626, 0.05494505, -0.17857143, -0.24725275],
            [0.05494505, -0.01373626, 0.49450549, -0.17857143, -0.24725275, 0.17857143, -0.3021978, 0.01373626],
            [0.01373626, -0.3021978, -0.17857143, 0.49450549, 0.17857143, -0.24725275, -0.01373626, 0.05494505],
            [-0.3021978, 0.01373626, -0.24725275, 0.17857143, 0.49450549, -0.17857143, 0.05494505, -0.01373626],
            [-0.01373626, 0.05494505, 0.17857143, -0.24725275, -0.17857143, 0.49450549, 0.01373626, -0.3021978],
            [-0.24725275, -0.17857143, -0.3021978, -0.01373626, 0.05494505, 0.01373626, 0.49450549, 0.17857143],
            [-0.17857143, -0.24725275, 0.01373626, 0.05494505, -0.01373626, -0.3021978, 0.17857143, 0.49450549]
        ], dtype=np.float64),

        # 1 5-------3 7
        #  |         |
        #  |         |
        #  |         |
        # 0 4-------2 6
        "yx_component": np.array([
            [ 0.49450549,  0.05494505, -0.3021978,  -0.24725275,  0.17857143,  0.01373626, -0.01373626, -0.17857143],
            [ 0.05494505,  0.49450549, -0.24725275, -0.3021978,  -0.01373626, -0.17857143,  0.17857143,  0.01373626],
            [-0.3021978,  -0.24725275,  0.49450549,  0.05494505,  0.01373626,  0.17857143, -0.17857143, -0.01373626],
            [-0.24725275, -0.3021978,   0.05494505,  0.49450549, -0.17857143, -0.01373626,  0.01373626,  0.17857143],
            [ 0.17857143, -0.01373626,  0.01373626, -0.17857143,  0.49450549, -0.3021978,   0.05494505, -0.24725275],
            [ 0.01373626, -0.17857143,  0.17857143, -0.01373626, -0.3021978,   0.49450549, -0.24725275,  0.05494505],
            [-0.01373626,  0.17857143, -0.17857143,  0.01373626,  0.05494505, -0.24725275,  0.49450549, -0.3021978 ],
            [-0.17857143,  0.01373626, -0.01373626,  0.17857143, -0.24725275,  0.05494505, -0.3021978,   0.49450549]
        ], dtype=np.float64),
    }
]