############################################################################
# WORKSPACE FOR DEVELOPING POSSIBLY USEFUL DORA FUNCTIONS. 
############################################################################

# you'll want some functions for grabbing predicates from LTM from both sym files and from memory states. 
# The functions should allow you to specify (a) an arity for what you want to grab, (b) a set of key semantics you want the preds attached to, (c) ... 
def grab_pred_sym(props, arity, key_sems):
    # iterate through props, and find preds with the right arity that have the key_sems. If you find relevant pred, then add the prop it comes from to the rels list. 
    rels = []
    for prop in props:
        go_on = False
        if len(prop['RBs']) == arity:
            go_on = True
        if go_on: 
            

def grab_pred_mem():
    # 




