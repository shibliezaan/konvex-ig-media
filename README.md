# konvex-ig-media

Public image hosting for the Konvex Instagram (konvex.marketing) daily business-news post.

- `tools/render_news.py news/<date>/card.json` renders `feed.jpg` (1080x1350) and `story.jpg` (1080x1920) in the Konvex brand style.
- `news/<YYYY-MM-DD>/` holds each day's card and images. Windsor posts them from
  `https://raw.githubusercontent.com/shibliezaan/konvex-ig-media/main/news/<date>/feed.jpg`.
- `news/log.json` lists every story already covered, so no news item is posted twice.

The repo must stay public, or Instagram can't fetch the images.
