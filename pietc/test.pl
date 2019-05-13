(define twice (lambda (x) (* 2 x)))
(define repeat (lambda (f) (lambda (x) (f (f x)))))
((repeat twice) 10)
;; (twice 10)
