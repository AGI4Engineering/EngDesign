SSD vendors typically use synthetic workloads to evaluate their SSD designs. These synthetic workloads are generated based on the
common storage-intensive workload patterns in common storage workloads (e.g., large sequential and random read/write workloads). Although these workloads are simple and static, they are designed to demonstrate an SSD upper-bound performance. In this problem, we start from analyzing synthetic workloads.

| Workload Type | R/W Ratio | IOSize | nthreads |
|:--------------|:----------|:--------|:----------|
| Sequential     | 0:1       | 4KB     | 16        |
| Sequential     | 1:0       | 4KB     | 16        |
| Random         | 0:1       | 4KB     | 1         |
| Random         | 1:0       | 4KB     | 1         |
| Random         | 0.5:0.5   | 4KB     | 16        |
| Random         | 0.5:0.5   | 16KB    | 16        |