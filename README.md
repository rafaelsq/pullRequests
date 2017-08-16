# BitBar GitHub PullRequests

1. copy `prs.5m.py` to yours bitbar folder
2. replace the username, owner, projects and ignore_labels with your data
3. done

If you want to change the icon color, you will have to generate new base64 image
1. create a new `index.html` with the content of `ico.png`
2. change the color(`fill` attribute)
3. use this function to generate the base64 image data; https://gist.github.com/rafaelsq/a9426f765d09e09b62f5dca67c3cb68d
4. remove the `data:image/png;base64` from the generated data and paste on `prs.5m.py`.
