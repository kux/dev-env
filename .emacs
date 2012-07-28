(transient-mark-mode 1)
(show-paren-mode 1)
(column-number-mode 1)
(setq scroll-step 1)
(ido-mode 1)

;; (set-default-font "-adobe-courier-medium-r-normal--14-100-100-100-m-90-iso10646-1")
(set-face-attribute 'default nil :height 95)

;; scrolling, parens, cursor, menu, and such:
(scroll-bar-mode nil)
(blink-cursor-mode nil)
(setq transient-mark-mode t)
(menu-bar-mode nil)
(tool-bar-mode nil)

;; no splash screen:
(setq inhibit-startup-message t)
(setq inhibit-splash-screen t)

;; (show-ws-toggle-show-trailing-whitespace)

(setq x-select-enable-clipboard t)
(setq interprogram-paste-function 'x-cut-buffer-or-selection-value)

(setq grep-find-command
      "find . -type f -not -path '*/.svn/*' -not -name '*.pyc' -not -name '*~' -not -name '*.orig' -not -name '*.rej' -print0 | xargs -0 -e grep -nH -P ")

(cua-selection-mode 1)

(put 'narrow-to-region 'disabled nil)

(put 'upcase-region 'disabled nil)
(put 'downcase-region 'disabled nil)


(when (load "flymake" t)
  (defun flymake-pyflakes-init ()
    (let* ((temp-file (flymake-init-create-temp-buffer-copy
                       'flymake-create-temp-inplace))
           (local-file (file-relative-name
                        temp-file
                        (file-name-directory buffer-file-name))))
      (list "lintrunner.py" (list local-file))
      ))
  (add-to-list 'flymake-allowed-file-name-masks   
               '("\\.py\\'" flymake-pyflakes-init)))

(load "~/.emacs.d/flymake-cursor.el")

(defun flymake-next-error (arg reset)
  (if (< arg 0)
      (flymake-goto-prev-error)
    (flymake-goto-next-error)))

(global-set-key (kbd "C-c n") 'flymake-goto-next-error)
(global-set-key (kbd "C-c p") 'flymake-goto-prev-error)

(defun enable-flymake ()
  (interactive)
  (flymake-mode 1)
  (setq next-error-function 'flymake-next-error))

(add-hook 'python-mode-hook
	  (lambda ()
	    (outline-minor-mode 1)
	    (light-symbol-mode)
            (which-function-mode t)))

(add-hook 'python-mode-hook
          (lambda ()
            (unless (eq buffer-file-name nil) (enable-flymake))))

(add-hook 'espresso-mode-hook
	  (lambda ()
	    (light-symbol-mode)))

(require 'yasnippet)
(yas/initialize)
(set-face-background  'yas/field-highlight-face "Grey50")
;; (set-face-background  'yas/mirror-highlight-face "Grey10")
(yas/load-directory "/usr/share/emacs/site-lisp/yasnippet/snippets")
(yas/load-directory "~/.emacs.d/yasnippets/snippets")

;; (global-set-key (kbd "C-c a") 'ecb-activate)
;; (global-set-key (kbd "C-c q") 'ecb-deactivate)

(load "~/.emacs.d/light-symbol.el")
(set-face-background  'hi-blue "Grey60")

(autoload #'espresso-mode "~/.emacs.d/espresso.el" "Start espresso-mode" t)
(add-to-list 'auto-mode-alist '("\\.js$" . espresso-mode))
(add-to-list 'auto-mode-alist '("\\.json$" . espresso-mode))

(setq-default indent-tabs-mode nil)

(setq require-final-newline nil)


(require 'uniquify)
(setq uniquify-buffer-name-style 'reverse)
(setq uniquify-separator "/")

(setq search-whitespace-regexp nil)

(load "~/.emacs.d/pretty-xml.el")
(global-set-key (kbd "C-c b") 'bf-pretty-print-xml-region)

(server-start)



;; autocompletion, take 3: (app-emacs/pymacs, ropemacs)

(require 'pymacs)
(pymacs-load "ropemacs" "rope-")
(global-set-key (kbd "C-c g") 'rope-goto-definition)
(global-set-key (kbd "C-/") 'dabbrev-expand)



(autoload 'django-html-mumamo-mode "~/.emacs.d/nxhtml/autostart.el")
(setq auto-mode-alist
      (append '(("\\.html?$" . django-html-mumamo-mode)) auto-mode-alist))
(setq mumamo-background-colors nil) 
(add-to-list 'auto-mode-alist '("\\.html$" . django-html-mumamo-mode))
;; Mumamo is making emacs 23.3 freak out:
(when (and (equal emacs-major-version 23)
           (equal emacs-minor-version 3))
  (eval-after-load "bytecomp"
    '(add-to-list 'byte-compile-not-obsolete-vars
                  'font-lock-beginning-of-syntax-function))
  ;; tramp-compat.el clobbers this variable!
  (eval-after-load "tramp-compat"
    '(add-to-list 'byte-compile-not-obsolete-vars
                  'font-lock-beginning-of-syntax-function)))
