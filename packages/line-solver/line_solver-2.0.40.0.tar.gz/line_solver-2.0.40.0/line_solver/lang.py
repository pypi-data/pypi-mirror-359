import jpype
import jpype.imports
import numpy as np
from pprint import pprint, pformat
from types import SimpleNamespace

from . import jlineMatrixToArray, jlineMapMatrixToArray, jlineMatrixFromArray
from .constants import *

"""
self.obj attribute in each class is a reference to the corresponding JLINE object
the methods invoked on self.obj are the JLINE methods exposed through JPype
"""


# Acts as a base class for specialized classes like OpenClass and ClosedClass
class JobClass:
    def __init__(self):
        pass

    def __index__(self):
        return self.obj.getIndex() - 1

    def getName(self):
        return self.obj.getName()


# Acts as a base class for specific node types like Queue, Source, etc.
class Node:
    def __init__(self):
        pass

    def setRouting(self, jobclass, strategy):
        self.obj.setRouting(jobclass.obj, strategy.value)

    def setProbRouting(self, jobclass, node, prob):
        self.obj.setProbRouting(jobclass.obj, node.obj, prob)

    def getName(self):
        return self.obj.getName()


# Specialized subclass of Node representing a station in the network
class Station(Node):
    def __init__(self):
        super().__init__()


# Defines the routing matrix of the network
# This matrix defines the probabilities of jobs transitioning between different nodes in the network
class RoutingMatrix:
    def __init__(self, rt):
        self.obj = rt  # references the Java RoutingMatrix object passed as argument

    def set(self, *argv):
        if len(argv) == 5:  # if 5 args are passed, it sets the routing probabilities between source and destination nodes for the specified classes
            class_source = argv[0]
            class_dest = argv[1]
            stat_source = argv[2]
            stat_dest = argv[3]
            prob = argv[4]
            return self.obj.set(class_source.obj, class_dest.obj, stat_source.obj, stat_dest.obj, prob)
        else:  # if 3 args are passed, it sets the routing probabilities for specified job classes
            class_source = argv[0]
            class_dest = argv[1]
            rt = argv[2]
            if isinstance(rt, RoutingMatrix):
                self.obj.set(class_source.obj, class_dest.obj, rt.obj)
            else:  # assume argv[2] is a np.array
                self.obj.set(class_source.obj, class_dest.obj, jlineMatrixFromArray(rt))
            return self.obj

    # This method sets the routing matrix for a given job class and a list of nodes
    def setRoutingMatrix(self, jobclass, node, pmatrix):
        if isinstance(jobclass, JobClass):  # single job class
            for i in range(len(node)):
                for j in range(len(node)):
                    self.set(jobclass, jobclass, node[i], node[j], pmatrix[i][j])
        else:  # multiple job classes
            for i in range(len(node)):
                for j in range(len(node)):
                    for k in range(len(jobclass)):
                        self.set(jobclass[k], jobclass[k], node[i], node[j], pmatrix[k][i][j])


# Represents a generic model in the network
class Model:
    def __init__(self):
        pass

    def getName(self):
        return self.obj.getName()

    def setName(self, name):
        self.obj.setName(name)

    def getVersion(self):
        return self.obj.getVersion()


# Data structure used to store the structural details of a queuing network
# Extracts and stores information about the network's components (nodes, stations, job classes, routin matrices etc.)
class NetworkStruct():
    # returns a human-readable string representation of the NetworkStruct object
    def __str__(self):
        return pformat(vars(self))

    # All attributes of NetworkStruct are populated when the below method is called with a jline network structure jsn passed as argument
    def fromJline(self, jsn):
        self.obj = jsn

        self.nstations = int(jsn.nstations)
        self.nstateful = int(jsn.nstateful)
        self.nnodes = int(jsn.nnodes)
        self.nclasses = int(jsn.nclasses)
        self.nclosedjobs = int(jsn.nclosedjobs)
        self.nchains = int(jsn.nchains)
        self.refstat = jlineMatrixToArray(jsn.refstat)
        self.njobs = jlineMatrixToArray(jsn.njobs)
        self.nservers = jlineMatrixToArray(jsn.nservers)
        self.connmatrix = jlineMatrixToArray(jsn.connmatrix)
        self.scv = jlineMatrixToArray(jsn.scv)
        self.isstation = jlineMatrixToArray(jsn.isstation)
        self.isstateful = jlineMatrixToArray(jsn.isstateful)
        self.isstatedep = jlineMatrixToArray(jsn.isstatedep)
        self.nodeToStateful = jlineMatrixToArray(jsn.nodeToStateful)
        self.nodeToStation = jlineMatrixToArray(jsn.nodeToStation)
        self.stationToNode = jlineMatrixToArray(jsn.stationToNode)
        self.stationToStateful = jlineMatrixToArray(jsn.stationToStateful)
        self.statefulToNode = jlineMatrixToArray(jsn.statefulToNode)
        self.rates = jlineMatrixToArray(jsn.rates)
        self.classprio = jlineMatrixToArray(jsn.classprio)
        self.phases = jlineMatrixToArray(jsn.phases)
        self.phasessz = jlineMatrixToArray(jsn.phasessz)
        self.phaseshift = jlineMatrixToArray(jsn.phaseshift)
        self.schedparam = jlineMatrixToArray(jsn.schedparam)
        self.chains = jlineMatrixToArray(jsn.chains)
        self.rt = jlineMatrixToArray(jsn.rt)
        self.nvars = jlineMatrixToArray(jsn.nvars)
        self.rtnodes = jlineMatrixToArray(jsn.rtnodes)
        self.csmask = jlineMatrixToArray(jsn.csmask)
        self.isslc = jlineMatrixToArray(jsn.isslc)
        self.cap = jlineMatrixToArray(jsn.cap)
        self.refclass = jlineMatrixToArray(jsn.refclass)
        self.lldscaling = jlineMatrixToArray(jsn.lldscaling)
        self.fj = jlineMatrixToArray(jsn.fj)
        self.classcap = jlineMatrixToArray(jsn.classcap)
        self.inchain = jlineMapMatrixToArray(jsn.inchain)
        self.visits = jlineMapMatrixToArray(jsn.visits)
        self.nodevisits = jlineMapMatrixToArray(jsn.nodevisits)
        self.classnames = tuple(jsn.classnames)
        self.nodetype = tuple(map(lambda x: NodeType.fromJLine(x), jsn.nodetype))
        self.nodenames = tuple(jsn.nodenames)

        sched = np.empty(int(jsn.nstations), dtype=object)
        space = np.empty(int(jsn.nstations), dtype=object)
        mu = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        phi = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        pie = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        proctype = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        droprule = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        proc = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses), 2), dtype=object)
        routing = np.empty(shape=(int(jsn.nnodes), int(jsn.nclasses)), dtype=object)
        nodeparam = np.empty(int(jsn.nnodes), dtype=object)
        # TODO: missing in Jline, rtorig always set to None?
        # rtorig = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        for ist in range(int(jsn.nstations)):
            sched[ist] = SchedStrategy(jsn.sched.get(jsn.stations[ist])).name
            space[ist] = jlineMatrixToArray(jsn.space.get(jsn.stations[ist]))
            for jcl in range(int(jsn.nclasses)):
                mu[ist, jcl] = jlineMatrixToArray(jsn.mu.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]))
                phi[ist, jcl] = jlineMatrixToArray(jsn.phi.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]))
                pie[ist, jcl] = jlineMatrixToArray(jsn.pie.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]))
                # rtorig[ist, jcl] = jlineMatrixToArray(jsn.rtorig.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]))
                proctype[ist, jcl] = ProcessType(jsn.proctype.get(jsn.stations[ist]).get(jsn.jobclasses[jcl])).name
                droprule[ist, jcl] = DropStrategy(jsn.droprule.get(jsn.stations[ist]).get(jsn.jobclasses[jcl])).name
                proc[ist, jcl, 0] = jlineMatrixToArray(jsn.proc.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]).get(0))
                proc[ist, jcl, 1] = jlineMatrixToArray(jsn.proc.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]).get(1))

        for ind in range(int(jsn.nnodes)):
            nodeparam[ind] = NodeParam(jsn.nodeparam.get(jsn.nodes[ind]))
            for jcl in range(int(jsn.nclasses)):
                routing[ind, jcl] = RoutingStrategy(jsn.routing.get(jsn.nodes[ind]).get(jsn.jobclasses[jcl])).name

        self.nodeparam = nodeparam
        self.sched = sched
        self.space = space
        self.mu = mu
        self.phi = phi
        self.pie = pie
        self.proctype = proctype
        self.routing = routing
        self.droprule = droprule
        # self.rtorig=rtorig
        self.proc = proc

        # TODO: fields missing in JLINE
        self.state = np.empty(int(jsn.nstateful), dtype=object)
        stateprior = np.empty(int(jsn.nstateful), dtype=object)
        for isf in range(int(jsn.nstateful)):
            self.state[isf] = jlineMatrixToArray(jsn.state.get(jsn.stateful.get(isf)))
            # stateprior[isf] = jlineMatrixToArray(jsn.state.get(jsn.stateprior[isf]))
        # self.state=state)
        # self.stateprior=stateprior)

        # TODO: fields not parsed yet
        # SerializableFunction<Pair<Map<Node, Matrix>, Map<Node, Matrix>>, Matrix> rtfun;
        # public Map<Station, Map<JobClass, SerializableFunction<Double, Double>>> lst;
        # public Map<Station, SerializableFunction<Matrix, Double>> cdscaling;
        # public Map<Integer, Sync> sync;

def NodeParam(jnodeparam):
    if jnodeparam is None or jnodeparam.isEmpty():
        return None

    typename = jnodeparam.getClass().getSimpleName()

    if typename == 'CacheNodeParam':
        return CacheNodeParam(jnodeparam)
    elif typename == 'ForkNodeParam':
        return ForkNodeParam(jnodeparam)
    elif typename == 'JoinNodeParam':
        return JoinNodeParam(jnodeparam)
    elif typename == 'RoutingNodeParam':
        return RoutingNodeParam(jnodeparam)
    elif typename == 'TransitionNodeParam':
        return TransitionNodeParam(jnodeparam)
    elif typename == 'ReplayerNodeParam':
        return ReplayerNodeParam(jnodeparam)
    elif typename == 'LoggerNodeParam':
        return LoggerNodeParam(jnodeparam)
    else:
        raise NotImplementedError(f'Unrecognized NodeParam type: {typename}')

class NodeParamBase:
    def __init__(self, jnodeparam, jclasses=None):
        self.jnodeparam = jnodeparam

        # Routing-related fields (now in the base Java class)
        self.weights = self._extract_class_matrix_map(jnodeparam.weights, jclasses)
        self.outlinks = self._extract_class_matrix_map(jnodeparam.outlinks, jclasses)
        self.withMemory = self._extract_class_matrix_map(jnodeparam.withMemory, jclasses)
        self.k = self._extract_class_int_map(jnodeparam.k, jclasses)

    def _extract_class_matrix_map(self, jmap, jclasses):
        if jmap is None or jclasses is None:
            return None
        result = {}
        for i in range(jclasses.size()):
            jclass = jclasses.get(i)
            if jmap.containsKey(jclass):
                result[str(jclass.getName())] = jlineMatrixToArray(jmap.get(jclass))
        return result if result else None

    def _extract_class_int_map(self, jmap, jclasses):
        if jmap is None or jclasses is None:
            return None
        result = {}
        for i in range(jclasses.size()):
            jclass = jclasses.get(i)
            if jmap.containsKey(jclass):
                result[str(jclass.getName())] = int(jmap.get(jclass))
        return result if result else None


class CacheNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)

        self.nitems = jnodeparam.nitems
        self.hitclass = jlineMatrixToArray(jnodeparam.hitclass)
        self.missclass = jlineMatrixToArray(jnodeparam.missclass)
        self.itemcap = jlineMatrixToArray(jnodeparam.itemcap)

        self.accost = [
            [jlineMatrixToArray(cell) if cell is not None else None for cell in row]
            for row in jnodeparam.accost
        ] if jnodeparam.accost is not None else None

        self.pread = {
            int(key): [float(v) for v in jnodeparam.pread.get(key)]
            for key in jnodeparam.pread.keySet()
        } if jnodeparam.pread is not None else None

        self.rpolicy = jnodeparam.rpolicy.name() if jnodeparam.rpolicy else None
        self.actualhitprob = jlineMatrixToArray(jnodeparam.actualhitprob)
        self.actualmissprob = jlineMatrixToArray(jnodeparam.actualmissprob)


class ForkNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.fanOut = jnodeparam.fanOut


class JoinNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.joinStrategy = jnodeparam.joinStrategy
        self.fanIn = jnodeparam.fanIn
        self.joinRequired = jnodeparam.joinRequired


class RoutingNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.weights = jnodeparam.weights
        self.outlinks = jnodeparam.outlinks
        self.withMemory = jnodeparam.withMemory
        self.k = jnodeparam.k


class TransitionNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.nmodes = jnodeparam.nmodes
        self.enabling = jnodeparam.enabling
        self.inhibiting = jnodeparam.inhibiting
        self.modenames = jnodeparam.modenames
        self.nmodeservers = jnodeparam.nmodeservers
        self.firing = jnodeparam.firing
        self.firingphases = jnodeparam.firingphases
        self.firingpie = jnodeparam.firingpie
        self.firingprocid = jnodeparam.firingprocid
        self.firingproc = jnodeparam.firingproc
        self.firingprio = jnodeparam.firingprio
        self.fireweight = jnodeparam.fireweight

class ReplayerNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.fileName = jnodeparam.fileName
        self.filePath = jnodeparam.filePath

class LoggerNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.fileName = jnodeparam.fileName
        self.filePath = jnodeparam.filePath
        self.startTime = jnodeparam.startTime
        self.loggerName = jnodeparam.loggerName
        self.timestamp = jnodeparam.timestamp
        self.jobID = jnodeparam.jobID
        self.jobClass = jnodeparam.jobClass
        self.timeSameClass = jnodeparam.timeSameClass
        self.timeAnyClass = jnodeparam.timeAnyClass


# A subclass of Model that represents a queuing network
class Network(Model):
    def __init__(self, *argv):
        super().__init__()
        # First argument defines either a JLINE network object or a valid network name from which a JLINE object is created
        if isinstance(argv[0], jpype.JPackage('jline').lang.Network):
            self.obj = argv[0]
        else:
            name = argv[0]
            self.obj = jpype.JPackage('jline').lang.Network(name)

    def serialRouting(*argv):
        ctr = 0
        if len(argv) == 1:
            rtlist = jpype.JPackage('jline').lang.nodes.Node[len(argv[0])]
            for arg in argv[0]:
                rtlist[ctr] = jpype.JObject(arg.obj, 'jline.lang.nodes.Node')
                ctr += 1
        else:
            rtlist = jpype.JPackage('jline').lang.nodes.Node[len(argv)]
            for arg in argv:
                rtlist[ctr] = jpype.JObject(arg.obj, 'jline.lang.nodes.Node')
                ctr += 1

        return RoutingMatrix(jpype.JPackage('jline').lang.Network.serialRouting(rtlist))

    def reset(self, hard=True):
        self.obj.reset(hard)

    def link(self, routing):
        self.obj.link(routing.obj)

    def relink(self, routing):
        self.obj.relink(routing.obj)

    def addLink(self, source, dest):
        self.obj.addLink(source.obj, dest.obj)

    def initRoutingMatrix(self):
        rt = self.obj.initRoutingMatrix()
        return RoutingMatrix(rt)

    def getNumberOfNodes(self):
        return self.obj.getNumberOfNodes()

    def getNumberOfStations(self):
        return self.obj.getNumberOfStations()

    def getNumberOfClasses(self):
        return self.obj.getNumberOfClasses()

    def getTranHandles(self):
        Qt, Ut, Tt = self.obj.getTranHandles()
        return Qt, Ut, Tt

    def jsimgView(self):
        from line_solver import SolverJMT
        SolverJMT(self).jsimgView()

    def jsimwView(self):
        from line_solver import SolverJMT
        SolverJMT(self).jsimgView()

    def addLinks(self, linkPairs):
        for i in range(len(linkPairs)):
            self.obj.addLink(linkPairs[i][0].obj, linkPairs[i][1].obj)

    def getStruct(self, force=True):
        jsn = self.obj.getStruct(force)
        sn = NetworkStruct()
        sn.fromJline(jsn)
        return sn

    # added
    def refreshStruct(self, hard=True):
        self.obj.refreshStruct(hard)

    def printRoutingMatrix(self):
        self.obj.printRoutingMatrix()

    def getProductFormParameters(self):
        # [arvRates, servDemands, nJobs, thinkTimes, ldScalings, nServers, visits] = model.getProductFormParameters()
        ret = self.obj.getProductFormParameters()
        return jlineMatrixToArray(ret.lambda_), jlineMatrixToArray(ret.D), jlineMatrixToArray(
            ret.N), jlineMatrixToArray(ret.Z), jlineMatrixToArray(ret.mu), jlineMatrixToArray(
            ret.S), jlineMatrixToArray(ret.V)

    """
    Defines static methods to create pre-define network structures
    """

    @staticmethod
    def tandemPsInf(lam, D, Z):
        return Network(
            jpype.JPackage('jline').lang.Network.tandemPsInf(jlineMatrixFromArray(lam), jlineMatrixFromArray(D),
                                                             jlineMatrixFromArray(Z)))

    @staticmethod
    def tandemFcfsInf(lam, D, Z):
        return Network(
            jpype.JPackage('jline').lang.Network.tandemFcfsInf(jlineMatrixFromArray(lam), jlineMatrixFromArray(D),
                                                               jlineMatrixFromArray(Z)))

    @staticmethod
    def tandemPs(lam, D):
        return Network(
            jpype.JPackage('jline').lang.Network.tandemPs(jlineMatrixFromArray(lam), jlineMatrixFromArray(D)))

    @staticmethod
    def tandemFcfs(lam, D):
        return Network(
            jpype.JPackage('jline').lang.Network.tandemPs(jlineMatrixFromArray(lam), jlineMatrixFromArray(D)))

    @staticmethod
    def cyclicPsInf(N, D, Z, S=None):
        if S is None:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicPs(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                              jlineMatrixFromArray(Z)))
        else:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicPs(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                              jlineMatrixFromArray(Z), jlineMatrixFromArray(S)))

    @staticmethod
    def cyclicFcfsInf(N, D, Z, S=None):
        if S is None:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicFcfs(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                                jlineMatrixFromArray(Z)))
        else:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicFcfs(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                                jlineMatrixFromArray(Z), jlineMatrixFromArray(S)))

    @staticmethod
    def cyclicPs(N, D, S=None):
        if S is None:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicPs(jlineMatrixFromArray(N), jlineMatrixFromArray(D)))
        else:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicPs(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                              jlineMatrixFromArray(S)))

    @staticmethod
    def cyclicFcfs(N, D, S=None):
        if S is None:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicFcfs(jlineMatrixFromArray(N), jlineMatrixFromArray(D)))
        else:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicFcfs(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                                jlineMatrixFromArray(S)))


class Cache(Node):
    def __init__(self, model, name, nitems, itemLevelCap, replPolicy, graph=()):
        super().__init__()
        if isinstance(itemLevelCap, int):
            if len(graph) == 0:
                self.obj = jpype.JPackage('jline').lang.nodes.Cache(model.obj, name, nitems,
                                                                    jpype.JPackage('jline').util.matrix.Matrix.singleton(
                                                                        itemLevelCap),
                                                                    replPolicy.value)
            else:
                self.obj = jpype.JPackage('jline').lang.nodes.Cache(model.obj, name, nitems,
                                                                    jpype.JPackage('jline').util.matrix.Matrix.singleton(
                                                                        itemLevelCap),
                                                                    replPolicy.value, graph)
        else:
            itemLevelCap = np.array(itemLevelCap, dtype=np.float64)
            if len(graph) == 0:
                self.obj = jpype.JPackage('jline').lang.nodes.Cache(model.obj, name, nitems,
                                                                    jpype.JPackage('jline').util.matrix.Matrix(
                                                                        itemLevelCap).colon().transpose(),
                                                                    replPolicy.value)
            else:
                self.obj = jpype.JPackage('jline').lang.nodes.Cache(model.obj, name, nitems,
                                                                    jpype.JPackage('jline').util.matrix.Matrix(
                                                                        itemLevelCap).colon().transpose(),
                                                                    replPolicy.value, graph)

    def setRead(self, jobclass, distrib):
        self.obj.setRead(jobclass.obj, distrib.obj)

    def setHitClass(self, jobclass1, jobclass2):
        self.obj.setHitClass(jobclass1.obj, jobclass2.obj)

    def setMissClass(self, jobclass1, jobclass2):
        self.obj.setMissClass(jobclass1.obj, jobclass2.obj)

    def getHitRatio(self):
        r = self.obj.getHitRatio()
        return r

    def getMissRatio(self):
        r = self.obj.getMissRatio()
        return r

"""
Abstracts for handling multi-stage systems
"""


# Represents a collection of models and acts as a base class for Env
class Ensemble:
    def __init__(self):
        pass

    def getModel(self, stagenum):
        return Network(self.obj.getModel(stagenum))

    def getEnsemble(self):
        jensemble = self.obj.getEnsemble()
        ensemble = np.empty(jensemble.size(), dtype=object)
        for i in range(len(ensemble)):
            ensemble[i] = Network(jensemble.get(i))
        return ensemble


# Specialized subclass of Ensemble that represents an environment with multiple stages and transitions between them
class Env(Ensemble):
    def __init__(self, name, nstages):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.Env(name, nstages)

    def addStage(self, stage, envname, envtype, envmodel):
        self.obj.addStage(stage, envname, envtype, envmodel.obj)

    def addTransition(self, envname0, envname1, rate):
        self.obj.addTransition(envname0, envname1, rate.obj)

    def getStageTable(self):
        # NOTE: Not implemented yet in  JLINE
        return self.obj.printStageTable()


# Specialized subclass of Station that represents a source node where jobs enter the network
class Source(Station):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Source(model.obj, name)

    def setArrival(self, jobclass, distribution):
        self.obj.setArrival(jobclass.obj, distribution.obj)


# Specialized subclass of Node that represents a logger node in the network (used to log eents and data related to the flow of jobs)
class Logger(Node):
    def __init__(self, model, name, logfile):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Logger(model.obj, name, logfile)

    # Enables/disables logging of the start time of jobs
    def setStartTime(self, activate):
        self.obj.setStartTime(activate)

    # Enables/disables logging of job IDs
    def setJobID(self, activate):
        self.obj.setJobID(activate)

    # Enables/disables logging of job classes
    def setJobClass(self, activate):
        self.obj.setJobClass(activate)

    # Enables/disables logging of timestamps
    def setTimestamp(self, activate):
        self.obj.setTimestamp(activate)

    # Enables/disables logging of the time spent by jobs in the same class
    def setTimeSameClass(self, activate):
        self.obj.setTimeSameClass(activate)

    # Enables/disables logging of the time spent by jobs in any class
    def setTimeAnyClass(self, activate):
        self.obj.setTimeAnyClass(activate)


# Specialized subclass of Node that represents a class switch node in the network
class ClassSwitch(Node):
    def __init__(self, *argv):
        model = argv[0]
        name = argv[1]
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.ClassSwitch(model.obj, name)
        if len(argv) > 2:
            csmatrix = argv[2]
            self.setClassSwitchingMatrix(csmatrix)

    def initClassSwitchMatrix(self):
        return jlineMatrixToArray(self.obj.initClassSwitchMatrix())

    def setClassSwitchingMatrix(self, csmatrix):
        self.obj.setClassSwitchingMatrix(jpype.JPackage('jline').lang.ClassSwitchMatrix(jlineMatrixFromArray(csmatrix)))


# Specialized subclass of Node that represents a sink node where jobs exit the network
class Sink(Node):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Sink(model.obj, name)


# Specialized subclass of Node that represents a fork node in the network
class Fork(Node):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Fork(model.obj, name)

    def setTasksPerLink(self, tasks):
        self.obj.setTasksPerLink(tasks)

# Specialized subclass of Station that represents a join station in the network
class Join(Station):
    def __init__(self, model, name, forknode):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Join(model.obj, name, forknode.obj)


# Specialized subclass of Station that represents a queue node in the network
class Queue(Station):
    def __init__(self, model, name, strategy):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Queue(model.obj, name, strategy.value)

    def setService(self, jobclass, distribution, weight=1.0):
        self.obj.setService(jobclass.obj, distribution.obj, weight)

    def setNumberOfServers(self, nservers):
        self.obj.setNumberOfServers(nservers)

    def setLoadDependence(self, ldscaling):
        self.obj.setLoadDependence(jlineMatrixFromArray(ldscaling))


# Specialized subclass of Station that represents a delay node in the network
class Delay(Station):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Delay(model.obj, name)

    def setService(self, jobclass, distribution):
        self.obj.setService(jobclass.obj, distribution.obj)


# Specialized subclass of Node that directs jobs to other nodes
class Router(Node):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Router(model.obj, name)


# Specialized subclass of JobClass that represents an open class of jobs
class OpenClass(JobClass):
    def __init__(self, model, name, prio=0):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.OpenClass(model.obj, name, prio)
        self.completes = True

    # Specialized method called whenever an attribute of an object is set
    # Ensures synchronisation/consistency between the Pythona and Java object representations
    def __setattr__(self, name, value):
        # ensures that the attribtue `name` is set to given `value` on the object
        object.__setattr__(self, name, value)
        if name == 'completes' and hasattr(self, 'completes'):
            if self.completes:
                self.obj.setCompletes(True)
            else:
                self.obj.setCompletes(False)


# Specialized subclass of JobClass that represents a closed class of jobs
class ClosedClass(JobClass):
    def __init__(self, model, name, njobs, refstat, prio=0):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.ClosedClass(model.obj, name, njobs, refstat.obj, prio)
        self.completes = True

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'completes' and hasattr(self, 'completes'):
            if self.completes:
                self.obj.setCompletes(True)
            else:
                self.obj.setCompletes(False)


# Specialized subclass of JobClass that represents a self-looping class of jobs
class SelfLoopingClass(JobClass):
    def __init__(self, model, name, njobs, refstat, prio=0):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.SelfLoopingClass(model.obj, name, njobs, refstat.obj, prio)
        self.completes = True

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'completes' and hasattr(self, 'completes'):
            if self.completes:
                self.obj.setCompletes(True)
            else:
                self.obj.setCompletes(False)


# Added a State class
class State:
    def __init__(self, initialState=None, priorInitialState=None):
        if initialState is not None and priorInitialState is not None:
            self.obj = jpype.JPackage('jline').lang.state.State(initialState, priorInitialState)
        else:
            self.obj = None

    @staticmethod
    def toMarginal(sn, ind, state_i, phasesz=None, phaseshift=None, space_buf=None, space_srv=None, space_var=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.toMarginal(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            state_i.obj if hasattr(state_i, 'obj') else state_i,
            phasesz.obj if phasesz is not None and hasattr(phasesz, 'obj') else phasesz,
            phaseshift.obj if phaseshift is not None and hasattr(phaseshift, 'obj') else phaseshift,
            space_buf.obj if space_buf is not None and hasattr(space_buf, 'obj') else space_buf,
            space_srv.obj if space_srv is not None and hasattr(space_srv, 'obj') else space_srv,
            space_var.obj if space_var is not None and hasattr(space_var, 'obj') else space_var,
        )
        # result is a StateMarginalStatistics object
        # convert to dict of Python arrays
        # marginal = {
        #     'ni': jlineMatrixToArray(result.ni) if hasattr(result, 'ni') and result.ni is not None else None,
        #     'nir': jlineMatrixToArray(result.nir) if hasattr(result, 'nir') and result.nir is not None else None,
        #     'sir': jlineMatrixToArray(result.sir) if hasattr(result, 'sir') and result.sir is not None else None,
        #     'kir': [jlineMatrixToArray(k) for k in result.kir] if hasattr(result, 'kir') and result.kir is not None else None,
        # }
        return result

    @staticmethod
    def fromMarginalAndStarted(sn, ind, n, s, optionsForce=True):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.fromMarginalAndStarted(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            n.obj if hasattr(n, 'obj') else n,
            s.obj if hasattr(s, 'obj') else s,
            bool(optionsForce)
        )
        # result is a Java matrix object
        # convert to Python array
        result = jlineMatrixToArray(result)
        return result


    @staticmethod
    def toMarginalAggr(sn, ind, state_i, K, Ks, space_buf=None, space_srv=None, space_var=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.toMarginalAggr(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            state_i.obj if hasattr(state_i, 'obj') else state_i,
            K.obj if hasattr(K, 'obj') else K,
            Ks.obj if hasattr(Ks, 'obj') else Ks,
            space_buf.obj if space_buf is not None and hasattr(space_buf, 'obj') else space_buf,
            space_srv.obj if space_srv is not None and hasattr(space_srv, 'obj') else space_srv,
            space_var.obj if space_var is not None and hasattr(space_var, 'obj') else space_var,
        )
        return result

    @staticmethod
    def fromMarginalAndRunning(sn, ind, n, s, optionsForce=False):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.fromMarginalAndRunning(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            n.obj if hasattr(n, 'obj') else n,
            s.obj if hasattr(s, 'obj') else s,
            bool(optionsForce)
        )
        result = jlineMatrixToArray(result)
        return result

    @staticmethod
    def isValid(sn, n, s):
        StateJava = jpype.JPackage('jline').lang.state.State
        return StateJava.isValid(
            sn.obj if hasattr(sn, 'obj') else sn,
            n.obj if hasattr(n, 'obj') else n,
            s.obj if hasattr(s, 'obj') else s
        )

    @staticmethod
    def fromMarginal(sn, ind, n):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.fromMarginal(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            n.obj if hasattr(n, 'obj') else n
        )
        result = jlineMatrixToArray(result)
        return result

    @staticmethod
    def afterEvent(sn, ind, inspace, event, jobClass, isSimulation=False, eventCache=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        if eventCache is not None:
            result = StateJava.afterEvent(
                sn.obj if hasattr(sn, 'obj') else sn,
                int(ind),
                inspace.obj if hasattr(inspace, 'obj') else inspace,
                event,
                int(jobClass),
                bool(isSimulation),
                eventCache
            )
        else:
            result = StateJava.afterEvent(
                sn.obj if hasattr(sn, 'obj') else sn,
                int(ind),
                inspace.obj if hasattr(inspace, 'obj') else inspace,
                event,
                int(jobClass),
                bool(isSimulation)
            )
        return result

    @staticmethod
    def isinf(matrix):
        StateJava = jpype.JPackage('jline').lang.state.State
        return StateJava.isinf(
            matrix.obj if hasattr(matrix, 'obj') else matrix
        )

    @staticmethod
    def cpos(matrix, i, j):
        StateJava = jpype.JPackage('jline').lang.state.State
        return StateJava.cpos(
            matrix.obj if hasattr(matrix, 'obj') else matrix,
            int(i),
            int(j)
        )

    @staticmethod
    def afterEventHashed(sn, ind, inspacehash, event, jobclass, isSimulation=False, options=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        if options is not None:
            result = StateJava.afterEventHashed(
                sn.obj if hasattr(sn, 'obj') else sn,
                int(ind),
                float(inspacehash),
                event,
                int(jobclass),
                bool(isSimulation),
                options
            )
        else:
            result = StateJava.afterEventHashed(
                sn.obj if hasattr(sn, 'obj') else sn,
                int(ind),
                float(inspacehash),
                event,
                int(jobclass),
                bool(isSimulation)
            )
        return result

    @staticmethod
    def spaceGenerator(sn, cutoff=None, options=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        if cutoff is not None and options is not None:
            result = StateJava.spaceGenerator(
                sn.obj if hasattr(sn, 'obj') else sn,
                cutoff.obj if hasattr(cutoff, 'obj') else cutoff,
                options.obj if hasattr(options, 'obj') else options
            )
        elif cutoff is not None:
            result = StateJava.spaceGenerator(
                sn.obj if hasattr(sn, 'obj') else sn,
                cutoff.obj if hasattr(cutoff, 'obj') else cutoff
            )
        else:
            result = StateJava.spaceGenerator(
                sn.obj if hasattr(sn, 'obj') else sn
            )
        return result

    @staticmethod
    def spaceClosedMultiCS(M, N, chains):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.spaceClosedMultiCS(
            int(M),
            N.obj if hasattr(N, 'obj') else N,
            chains.obj if hasattr(chains, 'obj') else chains
        )
        result = jlineMatrixToArray(result)
        return result

    @staticmethod
    def spaceClosedMulti(M, N):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.spaceClosedMulti(
            int(M),
            N.obj if hasattr(N, 'obj') else N
        )
        result = jlineMatrixToArray(result)
        return result

    @staticmethod
    def spaceGeneratorNodes(sn, cutoff=None, options=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        if cutoff is not None and options is not None:
            result = StateJava.spaceGeneratorNodes(
                sn.obj if hasattr(sn, 'obj') else sn,
                cutoff.obj if hasattr(cutoff, 'obj') else cutoff,
                options.obj if hasattr(options, 'obj') else options
            )
        elif cutoff is not None:
            result = StateJava.spaceGeneratorNodes(
                sn.obj if hasattr(sn, 'obj') else sn,
                cutoff.obj if hasattr(cutoff, 'obj') else cutoff
            )
        else:
            result = StateJava.spaceGeneratorNodes(
                sn.obj if hasattr(sn, 'obj') else sn
            )
        return result

    @staticmethod
    def fromMarginalBounds(sn, ind, n, nmax, s, smax):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.fromMarginalBounds(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            n.obj if hasattr(n, 'obj') else n,
            nmax.obj if hasattr(nmax, 'obj') else nmax,
            s.obj if hasattr(s, 'obj') else s,
            smax.obj if hasattr(smax, 'obj') else smax
        )
        result = jlineMatrixToArray(result)
        return result