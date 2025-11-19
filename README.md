# Pybrary of Babel

This project was inspired by the many implementations of the [Library of Babel](https://libraryofbabel.info/).

The goal of this repo is to:

- Sample random programs with the Library of Babel algorithm.
- Determine what percent of them are runnable.

## Quickstart.

Unfortunately, this code only works on a Linux system. 

This repo uses bubblewrap. Install that first. See [here](https://github.com/containers/bubblewrap). For me, just using `apt-get` worked:

``` bash
sudo apt-get install bubblewrap
```

Finally, we also require `uv`. See [here](https://docs.astral.sh/uv/) for the `uv` docs.

Then, try to fire up an experiment by checking out the CLI:

```bash
uv run pybrary-of-babel --help
```

## See also

Of course, you should read the original [Jorge Luis Borges short story](https://en.wikipedia.org/wiki/The_Library_of_Babel).

My introduction to this whole thing was actually [_A Short Stay In Hell_](https://en.wikipedia.org/wiki/A_Short_Stay_in_Hell). Which is heavily inspired by Borges's short story.
