(define twice (lambda (x) (* 2 x)))
(define repeat (lambda (f) (lambda (y) (f (f y)))))
;; (twice 20)
((repeat twice) 10)
