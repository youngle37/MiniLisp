(define fib (fun (x)
  (if (< x 2) x (+
                 (fib (- x 1))
                 (fib (- x 2))))))

(print-num (fib 1))
(print-num (fib 2))
(print-num (fib 3))
(print-num (fib 4))
(print-num (fib 5))
(print-num (fib 6))
(print-num (fib 7))
