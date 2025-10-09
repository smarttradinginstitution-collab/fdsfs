-- Aggiunge la colonna 'title' alla tabella 'news_impacts' per memorizzare il titolo dell'impatto della notizia.
ALTER TABLE public.news_impacts ADD COLUMN title VARCHAR(255);