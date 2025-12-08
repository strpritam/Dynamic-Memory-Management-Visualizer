🧠 Dynamic Memory Management Visualizer
📌 Project Overview

This project is a Dynamic Memory Management Visualizer built as part of our college curriculum to better understand how memory allocation and deallocation work inside an operating system.

Instead of learning these concepts only through theory, this project provides a visual and interactive way to see how memory blocks are allocated, used, and freed in real time.

🎯 Purpose of the Project

In Operating Systems, concepts like dynamic memory allocation, free memory blocks, and first-fit strategy are often difficult to imagine practically.
The main goal of this project is to:

Convert theoretical OS concepts into a visual simulation

Help students understand how memory is divided and managed

Show the effect of allocation and deallocation clearly

Bridge the gap between theory and real-world behavior

⚙️ How the System Works

The total memory is represented as a single continuous memory space

Memory is divided into blocks

Each block can be:

✅ Free

❌ Allocated (Used)

🔹 Allocation

When the user enters a block size and process label:

The system applies the First-Fit Allocation Algorithm

The first available free block large enough is selected

Memory is allocated and shown visually

🔹 Deallocation

The user can select an allocated block

That block is freed

The memory layout updates instantly

🔹 Visualization

🟢 Green blocks → Allocated memory

⚫ Dark blocks → Free memory

Logs are maintained to show allocation status and actions

🧩 Technologies Used
Frontend

HTML – Structure of the interface

CSS – Styling and responsive layout

JavaScript – User interaction and dynamic updates

Backend

Python (FastAPI) – Handles memory logic and API communication

WebSocket – Enables real-time updates between backend and frontend

💡 Key Features

Interactive memory visualization

Real-time updates using WebSockets

First-Fit memory allocation strategy

Allocation and deallocation logs

User-friendly and responsive interface

Educational and beginner-friendly design

📚 Educational Value

This project is especially useful for:

Computer Science students

Learning Operating Systems

Understanding Dynamic Memory Allocation

Visualizing abstract OS concepts easily

It helps students grasp concepts that are usually difficult to imagine by making them visible and interactive.

🧑‍🤝‍🧑 Team Contribution

This project was developed collaboratively.
Each member contributed to different aspects such as:

Backend logic

Frontend design

Code refactoring

UI improvements

Testing and debugging

✅ Conclusion

The Dynamic Memory Management Visualizer successfully demonstrates how memory is allocated and freed in an operating system using an easy-to-understand visual approach.
It serves as both a learning tool and a practical implementation of OS concepts taught in classrooms.
