{-# LANGUAGE RankNTypes #-}

import Data.Char
import System.Environment

newtype I = I {unI :: forall a. a -> (a -> a) -> (a -> a) -> a}

newtype L a = L {unL :: forall b. b -> (a -> b -> b) -> b}

reI z s p1s (I x) = snd $ x (I $ \z s p1s -> z, z) (\(x', _) -> (I $ \z s p1s -> s (unI x' z s p1s), s x')) (\(x', _) -> (I $ \z s p1s -> p1s (unI x' z s p1s), p1s x'))

reL n c (L l) = snd $ l (L $ \n c -> n, n) (\x (l', _) -> (L $ \n c -> c x (unL l' n c), c x l'))

instance Eq I where
  x == y = reI z s p1s x y
    where
      z y = unI y True (const False) (const False)
      s x' y = reI False (x' ==) (const False) y
      p1s x' y = reI False (const False) (x' ==) y

instance Eq a => Eq (L a) where
  x == y = reL n c x y
    where
      n y = unL y True (\_ _ -> False)
      c x xs y = reL False (\y ys -> x == y && xs == ys) y

fromInt 0 = I $ \z s p1s -> z
fromInt n
  | n `mod` 2 == 0 = I $ \z s p1s -> s (unI (fromInt (n `div` 2)) z s p1s)
  | otherwise = I $ \z s p1s -> p1s (unI (fromInt (n `div` 2)) z s p1s)

fromList [] = L $ \n c -> n
fromList (x : xs) = L $ \n c -> c x (unL (fromList xs) n c)

main = do
  args <- getArgs
  case args of
    [x] ->
      if flag == fromList (map (fromInt . ord) x)
        then putStrLn "correct"
        else putStrLn "incorrect"
    _ -> putStrLn "usage: scotty <flag>"

flag = L $ \n c -> c (I $ \z s p1s -> p1s (s (p1s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (s (s (s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (s (s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (p1s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (s (p1s (s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (s (p1s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (p1s (s (p1s (p1s (z))))))) (c (I $ \z s p1s -> s (s (s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (p1s (s (p1s (p1s (z))))))) (c (I $ \z s p1s -> s (p1s (p1s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (p1s (p1s (p1s (s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (s (s (p1s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (s (s (p1s (p1s (z))))))) (c (I $ \z s p1s -> p1s (s (p1s (s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (p1s (p1s (p1s (s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (p1s (s (p1s (p1s (z))))))) (c (I $ \z s p1s -> s (s (p1s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (s (s (p1s (p1s (z))))))) (c (I $ \z s p1s -> s (p1s (p1s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (p1s (s (p1s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (s (s (p1s (p1s (z))))))) (c (I $ \z s p1s -> p1s (p1s (p1s (p1s (p1s (s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (s (s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (s (p1s (s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (p1s (s (s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (s (s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (p1s (p1s (p1s (s (p1s (z))))))) (c (I $ \z s p1s -> s (s (p1s (s (s (s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (p1s (s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (p1s (s (s (p1s (s (p1s (z)))))))) (c (I $ \z s p1s -> s (p1s (p1s (s (p1s (s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (p1s (s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (s (p1s (p1s (s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (p1s (p1s (s (s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (s (p1s (s (s (p1s (z)))))))) (c (I $ \z s p1s -> s (p1s (p1s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> s (s (p1s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (s (p1s (p1s (s (s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (s (s (s (p1s (s (p1s (z)))))))) (c (I $ \z s p1s -> s (p1s (p1s (s (s (s (p1s (z)))))))) (c (I $ \z s p1s -> s (p1s (p1s (p1s (s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (p1s (p1s (s (p1s (p1s (p1s (z)))))))) (c (I $ \z s p1s -> p1s (s (p1s (s (p1s (p1s (z))))))) (c (I $ \z s p1s -> p1s (s (p1s (p1s (p1s (p1s (p1s (z)))))))) (n)))))))))))))))))))))))))))))))))))))))))))))))
