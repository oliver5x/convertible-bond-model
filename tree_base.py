from collections import deque
from abc import ABC, abstractmethod

class Node(ABC):
    def solve(self, **kwargs):
        if not self.isSolved():
            self._solveImplementation(**kwargs)

    def _solveImplementation(self, **kwargs):
        pass

    @abstractmethod
    def hasChilds(self):
        pass

    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def isSolved(self):
        pass

class TerminateNode(Node):
    def __init__(self, terminateValue=1):
        super().__init__()
        self.terminateValue = terminateValue

    def hasChilds(self):
        return False

    def value(self):
        return self.terminateValue

    def isSolved(self):
        return True


class AbsractNodeRole:

    def __init__(self, node):
        self.node = node

    def value(self):
        pass

class TerminateNodeRole(AbsractNodeRole):
    def __init__(self, val):
        self.val = val

    def value(self):
        return self.val

class IntermediateNodeRole(AbsractNodeRole):
    def __init__(self, node):
        super().__init__(node)

    def value(self):
        return self.node._valueImplementation()

class NodeRoleFactory:

    def __init__(self,node):
        self.node = node

    def buildRole(self):
        if not self.node.hasChilds():
            return TerminateNodeRole(self.node._valueImplementation())
        elif not self.node.parent:
            return IntermediateNodeRole(self.node)
        elif self.node.parent and not self.node.parent.isSolved():
            return TerminateNodeRole( self.node.terminateValue )
        else:
            return IntermediateNodeRole(self.node)

class BaseBinomialTree:
    def solve(self):
        self._preBuildTree()
        self.buildTree()
        self._postBuildTree()
        self._solveTree( self.targetValues() )

    def _preBuildTree(self):
        pass

    def buildTree(self, initialGuess=1.5):
        currentNodes = []
        for currentLevel in reversed(range(1,self.treeSize()+1)):
            lastNodes = currentNodes
            currentNodes = self._buildLevelNodes(currentLevel, self.treeSize(), lastNodes)

        self.tree = currentNodes[0] #First node of the tree

    def _postBuildTree(self):
        pass

    def _buildLevelNodes(self, currentLevel, totalSize, nextLevelNodes=None):
        pass

    def _solveTree(self, targetValues ):
        pass

    def treeSize(self):
        pass

    def targetValues(self):
        pass

    def nodesOfLevel(self, level):
        totalNodes    = int(((level+1)/2.0)*level)
        toIgnoreNodes = totalNodes - level
        stack = deque()
        stack.append( self.tree )
        for i in range(toIgnoreNodes):
            currentNode = stack.popleft()
            if not currentNode.low in stack:
                stack.append(currentNode.low)
            if not currentNode.up in stack:
                stack.append(currentNode.up)

        return stack

    def nodesByLevels(self, nodeToStart=None ):
        nodeToStart = nodeToStart or self.tree
        stack = deque()
        stack.append(nodeToStart)
        nodesByLevel=[]
        while (len(stack) > 0):
            currentNode = stack.popleft()
            nodesByLevel.append(currentNode)
            if currentNode.hasChilds():
                if not currentNode.low in stack:
                    stack.append(currentNode.low)
                if not currentNode.up in stack:
                    stack.append(currentNode.up)

        return nodesByLevel


