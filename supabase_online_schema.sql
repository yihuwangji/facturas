create extension if not exists pgcrypto;

create table if not exists public.invoice_uploads (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid(),
  file_name text not null,
  file_path text not null,
  mime_type text,
  status text not null default 'pending' check (status in ('pending', 'confirmed', 'ignored')),
  extracted_text text,
  parsed_data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.invoices_cloud (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid(),
  upload_id uuid references public.invoice_uploads(id) on delete set null,
  type text not null default 'expense',
  num text not null,
  date date,
  due date,
  supplier text,
  client text,
  nif text,
  description text,
  base numeric(12,2) not null default 0,
  iva_rate numeric(5,2) not null default 21,
  iva_amount numeric(12,2) not null default 0,
  irpf_rate numeric(5,2) not null default 0,
  irpf_amount numeric(12,2) not null default 0,
  total numeric(12,2) not null default 0,
  pay_method text,
  pay_date date,
  bank_amount numeric(12,2) not null default 0,
  cash_amount numeric(12,2) not null default 0,
  notes text,
  file_path text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists invoice_uploads_user_status_idx
  on public.invoice_uploads(user_id, status, created_at desc);

create index if not exists invoices_cloud_user_date_idx
  on public.invoices_cloud(user_id, date desc, created_at desc);

create index if not exists invoices_cloud_upload_id_idx
  on public.invoices_cloud(upload_id);

alter table public.invoice_uploads enable row level security;
alter table public.invoices_cloud enable row level security;

drop policy if exists "invoice_uploads_select_own" on public.invoice_uploads;
create policy "invoice_uploads_select_own"
  on public.invoice_uploads for select
  using ((select auth.uid()) = user_id);

drop policy if exists "invoice_uploads_insert_own" on public.invoice_uploads;
create policy "invoice_uploads_insert_own"
  on public.invoice_uploads for insert
  with check ((select auth.uid()) = user_id);

drop policy if exists "invoice_uploads_update_own" on public.invoice_uploads;
create policy "invoice_uploads_update_own"
  on public.invoice_uploads for update
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "invoices_cloud_select_own" on public.invoices_cloud;
create policy "invoices_cloud_select_own"
  on public.invoices_cloud for select
  using ((select auth.uid()) = user_id);

drop policy if exists "invoices_cloud_insert_own" on public.invoices_cloud;
create policy "invoices_cloud_insert_own"
  on public.invoices_cloud for insert
  with check ((select auth.uid()) = user_id);

drop policy if exists "invoices_cloud_update_own" on public.invoices_cloud;
create policy "invoices_cloud_update_own"
  on public.invoices_cloud for update
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

insert into storage.buckets (id, name, public)
values ('invoice-files', 'invoice-files', false)
on conflict (id) do nothing;

drop policy if exists "invoice_files_read_own" on storage.objects;
create policy "invoice_files_read_own"
  on storage.objects for select
  using (
    bucket_id = 'invoice-files'
    and (select auth.uid())::text = (storage.foldername(name))[1]
  );

drop policy if exists "invoice_files_insert_own" on storage.objects;
create policy "invoice_files_insert_own"
  on storage.objects for insert
  with check (
    bucket_id = 'invoice-files'
    and (select auth.uid())::text = (storage.foldername(name))[1]
  );

drop policy if exists "invoice_files_update_own" on storage.objects;
create policy "invoice_files_update_own"
  on storage.objects for update
  using (
    bucket_id = 'invoice-files'
    and (select auth.uid())::text = (storage.foldername(name))[1]
  )
  with check (
    bucket_id = 'invoice-files'
    and (select auth.uid())::text = (storage.foldername(name))[1]
  );
