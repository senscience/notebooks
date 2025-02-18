# FAIR² Portal Open Jupyter Notebooks

Welcome to the repository for **Open Jupyter Notebooks** supporting the **FAIR² Data Packages**. Each notebook provides an example of how to access and analyze the **FAIR² Data Package** associated with published **FAIR² Data Articles**. These notebooks demonstrate workflows for interacting with FAIR²-compliant datasets, enabling researchers to explore, visualize, and integrate data into their research.

## 📚 About FAIR² Data Packages

**FAIR² Data Packages** are comprehensive, FAIR-compliant datasets that extend the original FAIR principles by introducing:

- **AI-Readiness**: Optimized datasets for machine learning workflows.
- **Responsible AI Alignment**: Ensuring ethical and transparent data use.
- **Context-Rich Documentation**: Including provenance, methodologies, and detailed descriptions to ensure deep reusability.

These data packages accompany **FAIR² Data Articles** and are designed to make datasets not only findable and reusable but also interpretable and ready for advanced analysis.

## 🚀 Features of the Notebooks

- **Real-World Examples**: Demonstrations of how to access and analyze FAIR² Data Packages.
- **Reproducible Workflows**: Step-by-step instructions for exploring and processing data.
- **Interactive Visualizations**: Dynamic plots and charts to help make sense of the data.
- **Integration Tutorials**: Examples of how to integrate FAIR² datasets into external tools, APIs, and machine learning workflows.

## 📂 Repository Structure

Each notebook is stored in a directory that adheres to the following naming convention:

**Author-Year-Short Description**

This structure allows easy identification of the associated FAIR² Data Article.

```plaintext
/
├── Author-Year-ShortDescription/  # Directory for a specific notebook
│   ├── notebook.ipynb             # The Jupyter Notebook
│   ├── README.md                  # Summary of the notebook and related data
│   └── LICENSE                    # License for the notebook
├── requirements.txt               # Python dependencies for running notebooks
├── README.md                      # This file
└── LICENSE.md                     # License for the repository
```

## 🛠️ Getting Started

### Prerequisites

To use the notebooks, ensure you have the following installed:

- Python (>=3.8)
- Jupyter Notebook or JupyterLab
- Dependencies listed in `requirements.txt`

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/senscience/notebooks.git
   cd notebooks
   ```

2. **Install Dependencies:**

   Use `pip` to install required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Launch Jupyter:**

   ```bash
   jupyter notebook
   ```

   Open the desired notebook file from its corresponding directory to start exploring.

### Running in Google Colab

You can open any notebook directly in **Google Colab** without setting up a local environment.

1. **Locate the Notebook File:**  
   Navigate to the desired `.ipynb` notebook file in the repository on GitHub.

2. **Open in Google Colab:**
   - Click on the notebook file in the GitHub repository.
   - Copy the notebook’s URL from your browser.
   - Go to [Google Colab](https://colab.research.google.com/).
   - In Colab, select **File > Open Notebook**.
   - In the pop-up window, go to the **GitHub** tab, paste the notebook's URL, and press **Enter**.
   - Alternatively, you can directly modify the URL to prepend `https://colab.research.google.com/github/`.  
     For example:  
     ```text
     https://colab.research.google.com/github/senscience/notebooks/Author-Year-ShortDescription/notebook.ipynb
     ```

3. **Run the Notebook:**
   - Colab will automatically set up the environment.
   - Follow the instructions in the notebook to access and analyze the associated FAIR² Data Package.

## 📘 Documentation

For additional documentation on FAIR² and FAIR² Data Articles, visit [fair-squared.ai](https://fair-squared.ai).

## 🤝 Contribution Guidelines

We welcome contributions from the community to improve these notebooks!

### How to Contribute

1. **Fork the repository** and create your branch:
   ```bash
   git checkout -b feature/your-feature
   ```
2. **Make your changes**, ensuring they align with the repository's purpose and structure.
3. **Submit a pull request**, providing a clear description of the changes and their purpose.
4. Ensure your notebooks follow these standards:
   - Include comments explaining key steps.
   - Use Markdown cells for documentation within the notebook.
   - Add a `README.md` in the directory with a summary of the notebook's purpose.
   - Include a `LICENSE` file in the directory.

## 📜 License

This repository is licensed under the [Creative Commons Attribution 4.0 International License (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to use, modify, and distribute the contents, provided proper attribution is given.  
Each individual notebook directory will also contain its own license.

## 🧑‍🔬 Authors and Acknowledgments

This repository is maintained by the **FAIR² Team** at **SENSCIENCE**, with contributions from the global research community. Special thanks to all contributors who support the mission of advancing open science.

## 📬 Contact

For questions, suggestions, or feedback, please contact us at **support@senscience.ai**.  

We look forward to your contributions and engagement in building an open, FAIR²-aligned future for science!
