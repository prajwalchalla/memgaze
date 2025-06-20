// -*-Mode: C++;-*-

//***************************************************************************
//
// File:
//   $HeadURL$
//
// Purpose:
//   [The purpose of this file]
//
// Description:
//   [The set of functions, macros, etc. defined in the file]
//
//***************************************************************************

//************************* System Include Files ****************************
#ifndef MG_HPCTK_H
#define MG_HPCTK_H

#include <iostream>
#include <fstream>

#include <string>
using std::string;

#include <vector>

//#include <lib/profile/source.hpp>
//#include <tool/hpcprof/args.hpp>

#include <lib/profile/pipeline.hpp>
#include <lib/profile/source.hpp>
#include <lib/profile/scope.hpp>
#include <lib/profile/module.hpp>
#include <lib/profile/sinks/sparsedb.hpp>
#include <lib/profile/sinks/experimentxml4.hpp>
#include <lib/profile/finalizers/denseids.hpp>
#include <lib/profile/finalizers/directclassification.hpp>
#include <lib/profile/finalizers/struct.hpp>
#include <lib/profile/finalizer.hpp>
//#include <lib/prof-lean/hpcrun-fmt.h>
//#include <lib/prof/CallPath-Profile.hpp>
#include <lib/profile/stdshim/filesystem.hpp>

#include "Window.hpp"

using namespace hpctoolkit;
using namespace std;

int hpctk_realmain(int argc, char* const* argv, std::string struct_file, Window* fullT);
int hpctk_main(int argc, char* const* argv, std::string struct_file, Window* fullT);

class MemgazeSource final : public ProfileSource {
public:
  MemgazeSource(Window* fullT);
  ~MemgazeSource();

  Window* memgaze_root;
  string lm_name;
  unsigned long start_time;
 
  ThreadAttributes tattrs;
  ProfileAttributes attrs;
  PerThreadTemporary* thread;
  std::optional<ProfilePipeline::Source::AccumulatorsRef> accum;

  // struct to store contexts and their metrics
  struct ctx_info {
    Context& context;
    map<int, double> metrics;
  };
  vector<ctx_info> context_metrics;  

  // metrics mapping: <metric_type, metric object>
  map<int, Metric&> metrics;
  vector<reference_wrapper<Module>> modules;  
  vector<Function*> functions;

  // TODO: remove after being done with tests
  int num_contexts;
  int num_windows;
  int num_functions;
  int num_leaves;
  int num_samples;
  int num_of_sample_children;

  bool valid() const noexcept override;

  // Read in enough data to satisfy a request or until a timeout is reached.
  // See `ProfileSource::read(...)`.
  void read(const DataClass&) override;

  DataClass provides() const noexcept override;
  DataClass finalizeRequest(const DataClass&) const noexcept override;

  void numWindows(Window* node);
  void summarizeSample(Window* node, vector<Window*> &selected_leaves);
  void createCCT(Window* node, Module& lm, Context& parent_context);
  void addMetrics(string name, string description, int id);
//private:
};

class MemgazeFinalizers {
  public:
    MemgazeFinalizers() = default;
    ~MemgazeFinalizers() = default;
    
    class UnresolvedPaths final : public ProfileFinalizer {
    public:
      //UnresolvedPaths(MemgazeProfArgs& a) : args(a) {};
      UnresolvedPaths() = default;
      ~UnresolvedPaths() = default;

      ExtensionClass provides() const noexcept override { return ExtensionClass::resolvedPath; }
    
      ExtensionClass requires() const noexcept override { return {}; }
    
      std::optional<stdshim::filesystem::path> resolvePath(const File& f) noexcept override {
        return f.path();
      }
    
      std::optional<stdshim::filesystem::path> resolvePath(const Module& m) noexcept override {
        return m.path();
      }

    //private:
    //  MemgazeProfArgs& args;
    };

    class StatisticsExtender final : public ProfileFinalizer {
    public:
      //StatisticsExtender(MemgazeProfArgs& a) : args(a) {};
      StatisticsExtender() = default;
      ~StatisticsExtender() = default;

      ExtensionClass provides() const noexcept override {
        return ExtensionClass::statistics;
      }
    
      ExtensionClass requires() const noexcept override { return {}; }

      void appendStatistics(const Metric&, Metric::StatsAccess) noexcept override;
   
    //private:
    //  MemgazeProfArgs& args;
    };

    struct Stats final {
      bool sum : 1;
      bool mean : 1;
      bool min : 1;
      bool max : 1;
      bool stddev : 1;
      bool cfvar : 1;

      Stats() : sum(true), mean(false), min(false), max(false), stddev(false),
              cfvar(false) {};
    };
};

#endif
