# Interactive Cache Simulator & Performance Analyzer

An interactive web application built using **Python** and **Streamlit** to simulate cache memory behavior. The simulator demonstrates how different cache replacement and write policies affect cache performance and Effective Memory Access Time (EMAT).

## Features

- LRU (Least Recently Used) Replacement Policy
- FIFO (First-In First-Out) Replacement Policy
- Write Through Policy
- Write Back Policy
- Dirty Bit Handling
- Configurable Cache Size
- Configurable Block Size
- Cache Hit & Miss Tracking
- Effective Memory Access Time (EMAT) Calculation
- Step-by-Step Cache Simulation
- Cache State Visualization
- Upload Custom Memory Trace
- Random Trace Generation
- CSV Export for Simulation History
- Interactive Charts using Plotly

---

## Project Structure

```
cache-simulator/
│
├── app.py
├── cache.py
├── simulator.py
├── utils.py
├── sample_trace.txt
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd cache-simulator
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

---

## Input Trace Format

The simulator accepts traces in the following format:

```
10 Read
20 Write
30 Read
40 Write
```

Each line contains:

- Memory Address
- Operation (Read or Write)

---

## Cache Policies

### Replacement Policies

- LRU (Least Recently Used)
- FIFO (First-In First-Out)

### Write Policies

- Write Through
- Write Back

---

## Performance Metrics

The simulator reports:

- Total Memory Accesses
- Cache Hits
- Cache Misses
- Hit Rate
- Miss Rate
- Memory Writes
- Effective Memory Access Time (EMAT)

---

## Effective Memory Access Time

The simulator calculates:

```
EMAT = Hit Time + (Miss Rate × Memory Access Time)
```

---

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Graphviz

---

## Sample Screenshot

After running the simulator, the dashboard displays:

- Cache Configuration
- Performance Metrics
- Cache Visualization
- Step-by-Step Execution
- Simulation History
- EMAT Calculation
- CSV Export

---

## Future Improvements

Possible extensions include:

- Set Associative Cache
- Multi-Level Cache Simulation
- Random Replacement Policy
- LFU Replacement Policy
- Cache Address Breakdown
- Cache Miss Classification
- Memory Hierarchy Visualization

---

## Learning Outcomes

This project demonstrates concepts of:

- Computer Architecture
- Cache Memory
- Memory Hierarchy
- Data Structures
- Object-Oriented Programming
- Performance Analysis
- Interactive Data Visualization

---

## License

This project is intended for educational purposes.
