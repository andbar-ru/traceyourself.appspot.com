let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/GAE/traceyourself-hrd/src/resources
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +264 ~/GAE/traceyourself-hrd/src/quickfix.py
badd +5857 ~/GAE/traceyourself-hrd/src/resources/sun_and_moon_data.yaml
badd +871 ~/GAE/traceyourself-hrd/src/tasks.py
argglobal
silent! argdel *
argadd ~/GAE/traceyourself-hrd/src/tasks.py
edit ~/GAE/traceyourself-hrd/src/resources/sun_and_moon_data.yaml
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
wincmd _ | wincmd |
split
1wincmd k
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
exe 'vert 1resize ' . ((&columns * 135 + 134) / 269)
exe '2resize ' . ((&lines * 38 + 39) / 79)
exe 'vert 2resize ' . ((&columns * 133 + 134) / 269)
exe '3resize ' . ((&lines * 38 + 39) / 79)
exe 'vert 3resize ' . ((&columns * 133 + 134) / 269)
argglobal
setlocal fdm=marker
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 16 - ((15 * winheight(0) + 38) / 77)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
16
normal! 07|
wincmd w
argglobal
edit ~/GAE/traceyourself-hrd/src/quickfix.py
setlocal fdm=marker
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
3
normal! zo
45
normal! zo
49
normal! zo
45
normal! zc
254
normal! zo
254
normal! zc
923
normal! zo
924
normal! zo
923
normal! zc
let s:l = 566 - ((546 * winheight(0) + 19) / 38)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
566
normal! 01|
wincmd w
argglobal
edit ~/GAE/traceyourself-hrd/src/quickfix.py
setlocal fdm=marker
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
3
normal! zo
254
normal! zo
259
normal! zo
1059
normal! zo
let s:l = 288 - ((16 * winheight(0) + 19) / 38)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
288
normal! 031|
wincmd w
exe 'vert 1resize ' . ((&columns * 135 + 134) / 269)
exe '2resize ' . ((&lines * 38 + 39) / 79)
exe 'vert 2resize ' . ((&columns * 133 + 134) / 269)
exe '3resize ' . ((&lines * 38 + 39) / 79)
exe 'vert 3resize ' . ((&columns * 133 + 134) / 269)
tabnext 1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
