-- Create the youtube table to track uploaded videos
create table if not exists youtube (
  id uuid default uuid_generate_v4() primary key,
  song_id uuid references songs(id),
  youtube_id text unique,
  title text,
  description text,
  upload_date timestamp with time zone default now(),
  status text,
  view_count integer default 0,
  like_count integer default 0
);

-- Create index for faster lookups
create index if not exists youtube_song_id_idx on youtube(song_id);
create index if not exists youtube_youtube_id_idx on youtube(youtube_id);
create index if not exists youtube_status_idx on youtube(status);

-- Add comment to explain table purpose
comment on table youtube is 'Tracks videos uploaded to YouTube from the songs table';
