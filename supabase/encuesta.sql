-- Encuesta "¿Quién es quién?" de El Director. Del libro a la película
-- Ejecutar una vez en Supabase: SQL Editor → New query → pegar → Run.
-- Solo guarda el par elegido (personaje de la película, personaje del libro) y la fecha. Ningún dato personal.

create table if not exists public.votos (
  id     bigint generated always as identity primary key,
  peli   text not null check (peli in ('fernando', 'julio', 'elena', 'oskar', 'sara', 'pedro', 'virginia', 'marina', 'ortega', 'aurelio-ortiz', 'tesorero', 'julia', 'vidal', 'vicepresidenta', 'ministro')),
  libro  text not null check (libro in ('rajoy', 'saenz-de-santamaria', 'barcenas', 'villarejo', 'alierta', 'florentino-perez', 'pedro-j-ramirez', 'garcia-abadillo', 'botin', 'faine', 'sanchez-galan', 'francisco-gonzalez', 'urdangarin', 'inda', 'marhuenda', 'trinidad-jimenez', 'la-digna', 'la-favorita', 'rasputin', 'el-poeta', 'el-senorito', 'el-reportero', 'el-secretario', 'el-dos', 'el-viti', 'money', 'asuntos-internos', 'chupatintas', 'ninguno')),
  creado timestamptz not null default now()
);

-- Seguridad: cualquiera puede votar, nadie puede leer, cambiar ni borrar filas desde la web.
alter table public.votos enable row level security;
revoke all on public.votos from anon, authenticated;
grant insert (peli, libro) on public.votos to anon;
drop policy if exists "votar" on public.votos;
create policy "votar" on public.votos for insert to anon with check (true);

-- Resultados agregados (solo recuentos), lo único que la web puede leer.
create or replace function public.resultados()
returns table (peli text, libro text, votos bigint)
language sql stable security definer set search_path = public
as $$ select v.peli, v.libro, count(*)::bigint from public.votos v group by v.peli, v.libro $$;

revoke all on function public.resultados() from public;
grant execute on function public.resultados() to anon;
