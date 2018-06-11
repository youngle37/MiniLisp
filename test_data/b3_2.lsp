(define diff
  (fun (a b)
    (define abs
      (fun (a)
        (if (< a 0) (- 0 a) a)))
    (abs (- a b))))

(print-num (diff 1 10))
(print-num (diff 10 2))

