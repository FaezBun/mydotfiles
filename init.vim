# path: ~/.config/nvim/init.vim

set number
set relativenumber
set hlsearch
set incsearch
set tabstop=4
set shiftwidth=4
set expandtab
syntax on
set list
set autoindent
set smartindent
set ignorecase
set smartcase
set wrap
set linebreak
set listchars=tab:\|\ ,trail:-,nbsp:+
set omnifunc=htmlcomplete#CompleteTags

"coc.nvim"
set nobackup
set nowritebackup
set updatetime=300

" Paste ni juga untuk bagi warna garisan tu tak terlalu terang (lowkey)"
highlight SpecialKey ctermfg=darkgray guifg=gray

" Aktifkan syntax highlighting"
syntax on

"Vim kenal jenis file"
filetype plugin on

" Required for VimTeX to work properly"
filetype plugin indent on
syntax enable

" Set your viewer"
let g:vimtex_view_method = 'zathura'

call plug#begin()
Plug 'lervag/vimtex', {'tag': 'v2.15'} 
Plug 'neoclide/coc.nvim', {'branch': 'release'}
call plug#end()

nnoremap a i
nnoremap i a

set foldcolumn=4
highlight FoldColumn guibg=#282c34 guifg=#282c34 ctermbg=NONE ctermfg=NONE

" Margin Kanan (ColorColumn)
set colorcolumn=80
highlight ColorColumn guibg=#3e4451 ctermbg=237

if has('termguicolors')
    set termguicolors
endif

" Gunakan Tab untuk pilih senarai cadangan
inoremap <silent><expr> <TAB>
      \ pumvisible() ? "\<C-n>" :
      \ <SID>check_back_space() ? "\<TAB>" :
      \ coc#refresh()
inoremap <expr><S-TAB> pumvisible() ? "\<C-p>" : "\<C-h>"

function! s:check_back_space() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

" Gunakan Enter untuk sahkan pilihan cadangan daripada coc
inoremap <silent><expr> <CR> pumvisible() ? coc#_select_confirm() : "\<C-g>u\<CR>"

"Latar Belakang Lutsinar (Membolehkan gambar latar terminal kelihatan)"
autocmd ColorScheme * highlight Normal guibg=NONE ctermbg=NONE
autocmd ColorScheme * highlight NonText guibg=NONE ctermbg=NONE
colorscheme default
