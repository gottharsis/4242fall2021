# CX 4242 Fall 2021 Team 47

A visualization for COVID-19 vaccine side effects. 

This app is hosted online [here](cx4242fall2021.herokuapp.com). 
Note that due to the size of the dataset, the website will take a few minutes to render the visualizations. 

##Members: 
- Pushti Desai
- Aadarsh Govani
- Vishal Kobla
- Ayush Nene
- Christian Wilson



# Running this app
Note that the instructions below are for Linux (and maybe Mac). For windows, Git Bash might work, or if not, then be sure to use WSL.  

## Dependencies

### Yarn
Ensure you have [Yarn](https://yarnpkg.com/) installed.

### Poetry
Install [Poetry](https://python-poetry.org/), a dependency manager for Python. 

## Install the dependencies:
To install all the dependencies, run the following in the root: 
```
poetry install
```

```
cd client && yarn install
```

## Build and Run the app

To build the frontend, from the root directory, run (on a Linux or Mac)
```
cd client && yarn install && yarn build && cp -r build/* ../server/templates/
```

To run the app:
```
poetry run python wsgi.py
```



