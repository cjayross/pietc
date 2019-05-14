(define twice (lambda (x) (* 2 x)))
(define repeat (lambda (f) (lambda (y) (f (f y)))))
((repeat twice) 10)
;; ((if (eq? 1 1) twice (repeat twice)) 10)
