<!-- -*-Mode: markdown;-*- -->
<!-- $Id$ -->

MemGaze
=============================================================================

**Home**:
  - https://github.com/pnnl/memgaze

  - [Performance Lab for EXtreme Computing and daTa](https://github.com/perflab-exact)


**About**: As memory systems are the primary bottleneck in many
workloads, effective hardware/software co-design requires a detailed
understanding of memory behavior. Unfortunately, current analysis of
word-level sequences of memory accesses incurs time slowdowns of
O(100×).

MemGaze is a memory analysis toolset that combines high-resolution
trace analysis and low overhead measurement, both with respect to time
and space.

MemGaze provides high-resolution by collecting world-level memory
access traces, where the highest resolution supported is back-to-back
sequences. In particular, it leverages emerging Processor Tracing
support to collect data. It achieves low-overhead in space and time by
leveraging sampling and various methods of hardware support for
collecting traces.

MemGaze provides several post-mortem trace processing methods,
including multi-resolution analysis for locations vs. operations;
accesses vs. spatio-temporal reuse, and reuse (distance, rate, volume)
vs. access patterns.

Memgaze now includes MemFriend, a new analysis module that introduces
spatial and temporal locality analysis that captures affinity (access
correlation) between pairs of memory locations. MemFriend's
multi-resolution analysis identifies significant memory segments and
simultaneously prunes the analysis space such that time and space
complexity is modest. MemFriend creates signatures, selectable at 3D,
2D, and 1D resolutions, that provide novel insights and enable
predictive reasoning about application performance. The results aid
data layout optimizations, and data placement decisions.


**Contacts**: (_firstname_._lastname_@pnnl.gov)
  - Nathan R. Tallent ([www](https://hpc.pnnl.gov/people/tallent)), ([www](https://www.pnnl.gov/people/nathan-tallent))


**Contributors**:
  - Nathan R. Tallent (PNNL) ([www](https://hpc.pnnl.gov/people/tallent)), ([www](https://www.pnnl.gov/people/nathan-tallent))
  - Yasodha Suriyakumar (Portland State University)
  - Ozgur Kilic (Now BNL)
  - Andrés Marquez (PNNL)
  - Onur Cankur (University of Maryland)
  - Chenhao Xie (PNNL)
  - Stephane Eranian (Google)


References
-----------------------------------------------------------------------------

* Yasodha Suriyakumar, Nathan R. Tallent, Andrés Marquez, and Karen Karavanic, "MemFriend: Understanding memory performance with spatial-temporal affinity," in Proc. of the International Symposium on Memory Systems (MemSys 2024), September 2024.

* Ozgur O. Kilic, Nathan R. Tallent, Yasodha Suriyakumar, Chenhao Xie, Andrés Marquez, and Stephane Eranian, "MemGaze: Rapid and effective load-level memory and data analysis," in Proc. of the 2022 IEEE Conf. on Cluster Computing, IEEE, Sep 2022.

* Ozgur O. Kilic, Nathan R. Tallent, and Ryan D. Friese, "Rapid memory footprint access diagnostics," in Proc. of the 2020 IEEE Intl. Symp. on Performance Analysis of Systems and Software, IEEE Computer Society, May 2020. <https://10.1109/ISPASS48437.2020.00047>

* Ozgur O. Kilic, Nathan R. Tallent, and Ryan D. Friese, "Rapidly measuring loop footprints," in Proc. of IEEE Intl. Conf. on Cluster Computing (Workshop on Monitoring and Analysis for High Performance Computing Systems Plus Applications), pp. 1--9, IEEE Computer Society, September 2019. https://doi.org/10.1109/CLUSTER.2019.8891025


Acknowledgements
-----------------------------------------------------------------------------

This work was supported by the U.S. Department of Energy's Office of
Advanced Scientific Computing Research:

- Orchestration for Distributed & Data-Intensive Scientific Exploration

- Advanced Memory to Support Artificial Intelligence for Science

