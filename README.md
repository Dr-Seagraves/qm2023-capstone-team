[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gp9US0IQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22634860&assignment_repo_type=AssignmentRepo)
# QM 2023 Capstone Project

Semester-long capstone for Statistics II: Data Analytics.

## Project Structure

- **code/** — Python scripts and notebooks. Use `config_paths.py` for paths.
- **data/raw/** — Original data (read-only)
- **data/processed/** — Intermediate cleaning outputs
- **data/final/** — M1 output: analysis-ready panel
- **results/figures/** — Visualizations
- **results/tables/** — Regression tables, summary stats
- **results/reports/** — Milestone memos
- **tests/** — Autograding test suite

Run `python code/config_paths.py` to verify paths.

Team Members and Roles
> Sam Weber (idk)
> Brett
> Anthony


Research Question: 

> What is driving the divergence between different asset classes (cash, stocks, bonds, gold, and real estate)? How well can economic data predict the performance of these asset classes? How do the variable's coefficients vary over time (ie 5 year stretches)? How can pricing of assets in terms of alternative assets affect how we view them (ie S&P 500 in gold terms vs in USD)?

Dataset Overview:

> Primary Data:

    Stocks (S&P 500)
    Bonds (10 year treasury)
    Real Estate (Case-Shiller home price index)
    Gold (Gold spot price)

> Supplementary Data:

    Monetary Policy (M1, M2)
    Interest rates (Federal funds rate, Real rates, Yield curve slope)
    Inflation (CPE, PCI)
    Economic Activity (US GDP, Unemployment rate)
    Credit Conditions (Mortgage rates, BBB - treasury spread)
    Risk (VIX, Economic policy uncertainty index, DXY)
    Market Sentiment (Consumer confidence index, Michigan consumer sentiment index)



