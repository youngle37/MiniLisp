(print-num (* 1 2 3 4 5))
(print-bool #t)
(print-bool ((fun (x y) (= x y)) 2 5))
(define www (+ 1 2 3 4 5))
(print-num www)
(define fact (fun (n)
                  (if (< n 3)
                    n
                    (* n (fact (- n 1)))
                    )
                  ))
(print-num (fact 10))
(define chose (fun (chose-fun x y)
                   (if (chose-fun x y)
                     x
                     y
                     )
                   ))
(print-num (chose (fun (x y) (> x y)) 2 1))
(define dist-square
  (fun (x y)
       (define square
         (fun (x) (* x x)))
       (+ (square x) (square y))))
(print-num (dist-square 5 6))
(define add-x (fun (x) (fun (y) (+ x y))))
(define z (add-x 10))
(print-num (z 1))
