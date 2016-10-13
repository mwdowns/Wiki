from flask import Flask, render_template, request, redirect
import pg
app = Flask("album stuff")

db = pg.DB(dbname="music_db")

@app.route("/album/<int:album_id>")
def album_info(album_id):
    query = db.query("""
    select
        album.id,
        album.name,
        album.year,
        artist.name as artist_name
    from
        album, featured, artist
    where
        album.id = %d and featured.artist_id = artist.id and featured.album_id = album.id
    """ % album_id)
    result_list = query.namedresult()
    album = result_list[0]
    return render_template(
        "album_info.html",
        album=album
    )

if __name__ == "__main__":
    app.run(debug=True)
