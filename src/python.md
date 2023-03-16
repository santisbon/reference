# Python

[Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)  

## Install Python, the pip Python package installer, and Setuptools
### With Homebrew
Even if you already have Python on your OS it might be an outdated version. This installs python and pip.  
macOS
```zsh
brew install python
python3 --version
```
The python formulae install pip (as pip3) and Setuptools. Setuptools can be updated via pip3 and pip3 can be used to upgrade itself.
```zsh
python3 -m pip install --upgrade setuptools
python3 -m pip install --upgrade pip
```
Add the unversioned symlinks to your `$PATH` by adding this to your `.zshrc` file.
```zsh
export PATH="$(brew --prefix)/opt/python/libexec/bin:$PATH"
```
See the [Homebrew Python](https://docs.brew.sh/Homebrew-and-Python) documentation for details.  

`site-packages` is here. Example for python 3.10 on Homebrew
```zsh
ls -al $(brew --prefix)/lib/python3.10/site-packages
```

### Without Homebrew
Linux (Ubuntu)
```zsh
sudo apt install python3
```

macOS  
Download .pkg installer from pythong.org. Then get pip.
```zsh
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
```

Linux
```zsh
sudo apt install python-pip
```

```zsh
pip install --upgrade pip setuptools
```
On Ubuntu, upgrading to pip 10 may break pip. If this happens you need to:
```zsh
sudo nano /usr/bin/pip
# change "from pip import main" to "from pip._internal import main"
```

## Get the pep8 python style checker
```zsh
# On Linux you may need to use sudo.
pip install pep8
```

## Anaconda
For data science and machine learning. [Anaconda](https://docs.anaconda.com/anaconda/) is a distribution of the Python and R programming languages for scientific computing. See [Getting Started](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html).
```zsh
brew install --cask anaconda
```

[Installing in silent mode](https://docs.anaconda.com/anaconda/install/silent-mode/)  

Add anaconda to your `PATH` on your `.zshrc` and `source ~/.zshrc` to apply the changes.
```zsh
export PATH="$(brew --prefix)/anaconda3/bin:$PATH"
```
To use zsh:
```zsh
conda init zsh
```
If `conda init zsh` messed up the `PATH` in your `~/.zshrc` by adding the `condabin` directory instead of `bin` you can fix it with a symlink:
```zsh
ln -sf $(brew --prefix)/anaconda3/bin/jupyter-lab $(brew --prefix)/anaconda3/condabin/jupyter-lab
ln -sf $(brew --prefix)/anaconda3/bin/jupyter $(brew --prefix)/anaconda3/condabin/jupyter
```

If you don't want to activate the `base` environment every time you open your terminal:
```zsh
conda config --set auto_activate_base false
```

When creating a conda environment you can use optionally use a configuration file. You can also of course, save a config file from an existing environment to back it up.
```zsh
conda env create -f myenv.yml
conda activate myenv

conda env list
conda env remove --name ldm
```

### Notebooks
Fresh installs of Anaconda no longer include notebook extensions in their Jupyter installer. This means that the nb_conda libraries need to be added into your environment separately to access conda environments from your Jupyter notebook. Just run these to add them and you should be able to select your environment as a kernel within a Jupyter notebook.
```zsh
conda activate <myenv>
conda install ipykernel
conda install nb_conda_kernels # or defaults::nb_conda_kernels
```

Now you can launch the new JupyterLab or the classic Jupyter Notebook.
```zsh
jupyter-lab # or the classic "jupyter notebook"
```

