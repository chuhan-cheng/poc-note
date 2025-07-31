package main

import (
	"runtime"
	"sync"
)

func busyLoop(wg *sync.WaitGroup) {
	defer wg.Done()
	for {
		// 空轉，持續消耗 CPU
	}
}

func main() {
	numCPU := runtime.NumCPU()
	runtime.GOMAXPROCS(numCPU) // 設定使用所有 CPU 核心

	var wg sync.WaitGroup
	wg.Add(numCPU)

	for i := 0; i < numCPU; i++ {
		go busyLoop(&wg)
	}

	wg.Wait()
}
