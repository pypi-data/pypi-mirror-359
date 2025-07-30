PYTHONS_MUSICALS
=======

|img1| https://i.pinimg.com/originals/0f/4e/86/0f4e86b2085cecc78942b05279c961d3.png
+--------+
| |img1| |
+--------+

## About

This Python's library can "play" the notes and she can download YOUR music.

It's got two modules: `note` and `load_music`

## Installing
Enter in your bash:
```bash
pip install pythons_musicals
```

## Call the functions

Note module's call is:

```py
import pythons_musicals

<yourNoteVariable> = pythons_musicals.note.load(<note>)

if __name__ == "__main__":
    <yourNoteVariable>.play()
```

and load_music module's call is:

```py

    import pythons_musicals

    <SoundVariable> = pythons_muscals.load_music.load(<yourDirectory>)

    if __name__ == "__main__":
        <SoundVariable>.start()
```

ATTENTION!
------

Note module's got method `play()`, and load_music module's got method `start()`