# vse_batch_util
application of arbitrary command to selected image sequence

For now it is just a proof of concept to myself.  Very much a programmer's interface and not yet a user's interface.

But in theory it should work on multiple platforms, as long as gmic is installed.

The input directory and output directory need to be specified but there is an example command that of hopefully significant enough complexity to get someone started.

You write a gmic command-line command using a bit of extra python templating syntax and you get an auto-magic ui from the command ... but ... it resets when you change the command.  Still working on that and other features like intelligent sorting and re-arranging of frames ( so many naming schemes / collation is hard )
