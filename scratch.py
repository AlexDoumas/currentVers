

# function to check if you should make a new semantic unit. 
def checkMakeNewSem(semantic, memory):
    makeNewSem = True
    # is the semantic in a list or not?
    if type(semantic) is list:
        for oldsemantic in semantics:
            if oldsemantic.name == memory.semantic[0]:
                makeNewSem = False
                newSem = oldsemantic
                break
    else:
        for oldsemantic in semantics:
            if oldsemantic.name == memory.semantic:
                makeNewSem = False
                newSem = oldsemantic
                break
    # done. 
    return makeNewSem



# function to set up a semantic connection, making a new semantic if needed. 
def setupSemantic(makeNewSem, newPO, memory):
    if makeNewSem:
        # create the new semantic and the newLink.
        # ekaterina: check whether semantic is higher order; template for ho sems: [['ho_sem_name1', 1, None, None, 'HO', ['name11', 'name12', 'name13'], ['ho_sem_name2', 1, None, None, 'HO', ['name21', 'name22', 'name23']]
        ############### HERE ##############
        if (type(semantic) is list) and (len(semantic) > 5): # ekaterina
            newSem = dataTypes.Semantic(semantic[0], semantic[2], semantic[3], semantic[4])
            newLink = dataTypes.Link(newPO, None, None, newSem, semantic[1])
            # ekaterina: if newSem is higher order semantic, semantic[5] contains a list of regular semantics it is connected to; create sem-ho_sem connections; first check whether regular semantics are already in memory
            for regSemName in semantic[5]: # ekaterina
                makeRegSem = True
                for oldsemantic in memory.semantics:
                    if regSemName == oldsemantic.name:
                        makeRegSem = False
                        regSem = oldsemantic
                        break
                if makeRegSem: # this regular semantic is not yet in memory and needs to be recruited
                    regSem = dataTypes.Semantic(regSemName)
                    memory.semantics.append(regSem)
                # connect regular semantic to higher order semantic
                if newSem not in regSem.semConnect:
                    regSem.semConnect.append(newSem)
                newSem.semConnect.append(regSem)
                # update weight of the sem-ho_sem connection
                myIndex = newSem.semConnect.index(regSem)
                newSem.semConnectWeights[myIndex] = 1
        # check wheter semantic codes a dimension or not.
        elif (type(semantic) is list) and (len(semantic) > 4):
            newSem = dataTypes.Semantic(semantic[0], semantic[2], semantic[3], semantic[4])
            newLink = dataTypes.Link(newPO, None, None, newSem, semantic[1])
        elif (type(semantic) is list) and (len(semantic) > 2):
            newSem = dataTypes.Semantic(semantic[0], semantic[2], semantic[3])
            newLink = dataTypes.Link(newPO, None, None, newSem, semantic[1])
        elif type(semantic) is list:
            newSem = dataTypes.Semantic(semantic[0])
            newLink = dataTypes.Link(newPO, None, None, newSem, semantic[1])
        else:
            # default to a semantic with a weight of 1.
            newSem = dataTypes.Semantic(semantic)
            newLink = dataTypes.Link(newPO, None, None, newSem, 1)
        # add newLink to newSem and newPred, and add newLink to currentLinks, and newSem to memory.semantics.
        newSem.myPOs.append(newLink)
        newPO.mySemantics.append(newLink)
        memory.Links.append(newLink)
        memory.semantics.append(newSem)
    else: # the semantic already exists.
        # create the newLink.
        # if semantic is a list, then use semantic[1] for the weight, else default to a weight of 1.
        if type(semantic) is list:
            newLink = dataTypes.Link(newPO, None, None, newSem, semantic[1])
        else:
            newLink = dataTypes.Link(newPO, None, None, newSem, 1)
        # add newLink to newSem and newPred, and add newLink to currentLinks, (don't need to add newSem to memory.semantics because it is already there (remember that makeNewSem == False)).
        newSem.myPOs.append(newLink)
        newPO.mySemantics.append(newLink)
        memory.Links.append(newLink)
    # done. 
    return newPO, memory





