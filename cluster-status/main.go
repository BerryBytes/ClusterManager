package main

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/sirupsen/logrus"
	v1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/fields"
	"k8s.io/apimachinery/pkg/util/runtime"
	"k8s.io/apimachinery/pkg/util/wait"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/util/workqueue"
	"k8s.io/klog"
)

type Controller struct {
	indexer  cache.Indexer
	queue    workqueue.RateLimitingInterface
	informer cache.Controller
}

func NewController(queue workqueue.RateLimitingInterface, indexer cache.Indexer, informer cache.Controller) *Controller {
	return &Controller{
		informer: informer,
		indexer:  indexer,
		queue:    queue,
	}
}

func (c *Controller) processNextItem() bool {
	// Wait until there is a new item in the working queue
	key, quit := c.queue.Get()
	if quit {
		return false
	}
	// Tell the queue that we are done with processing this key. This unblocks the key for other workers
	// This allows safe parallel processing because two pods with the same key are never processed in
	// parallel.
	defer c.queue.Done(key)

	// Invoke the method containing the business logic
	err := c.syncToStdout(key.(string))
	// Handle the error if something went wrong during the execution of the business logic
	c.handleErr(err, key)
	return true
}

// syncToStdout is the business logic of the controller. In this controller it simply prints
// information about the pod to stdout. In case an error happened, it has to simply return the error.
// The retry logic should not be part of the business logic.
func (c *Controller) syncToStdout(key string) error {
	obj, exists, err := c.indexer.GetByKey(key)
	if err != nil {
		klog.Errorf("Fetching object with key %s from store failed with %v", key, err)
		return err
	}

	if !exists {
		// Below we will warm up our cache with a Pod, so that we will see a delete for one pod
		fmt.Printf("Pod %s does not exist anymore\n", key)
	} else {
		pod := obj.(*v1.Pod)
		// Note that you also have to check the uid if you have a local controlled resource, which
		// is dependent on the actual instance, to detect that a Pod was recreated with the same name
		// fmt.Printf("Sync/Add/Update for Pod %s  Status %v \n ", pod.GetName(), pod.Status.Phase)
		// fmt.Printf("Sync/Add/Update for Pod %s Status %v Label {\"status-controller-vcluster\": \"cluster-manager\"}\n", pod.GetName(), pod.Status.Phase)
		if pod.Labels["status-controller-vcluster"] == "cluster-manager" {
			for key, value := range pod.ObjectMeta.Labels {
				if key == "status-controller" {
					// Extract the specific container status
					statusString := ""
					for _, containerStatus := range pod.Status.ContainerStatuses {
						containerState := containerStatus.State

						if containerState.Waiting != nil {
							waitingReason := containerState.Waiting.Reason
							switch waitingReason {
							case "ImagePullBackOff":
							case "OOMKilled":
							case "ContainerConfigError":
							case "CrashLoopBackOff":
								statusString = waitingReason
							default:
								statusString = "Pending"
							}
						} else if containerState.Running != nil {
							statusString = "Running"
						} else if containerState.Terminated != nil {
							statusString = "Stopped"
						} else {
							statusString = "Failed"
						}
					}
					fmt.Printf("Container %s Status: %s\n", pod.Name, statusString)
					patchClusterStatus(pod.Name, value, statusString)
				}
			}
		}

	}
	return nil
}

// handleErr checks if an error happened and makes sure we will retry later.
func (c *Controller) handleErr(err error, key interface{}) {
	if err == nil {
		// Forget about the #AddRateLimited history of the key on every successful synchronization.
		// This ensures that future processing of updates for this key is not delayed because of
		// an outdated error history.
		c.queue.Forget(key)
		return
	}

	// This controller retries 5 times if something goes wrong. After that, it stops trying.
	if c.queue.NumRequeues(key) < 5 {
		klog.Infof("Error syncing pod %v: %v", key, err)

		// Re-enqueue the key rate limited. Based on the rate limiter on the
		// queue and the re-enqueue history, the key will be processed later again.
		c.queue.AddRateLimited(key)
		return
	}

	c.queue.Forget(key)
	// Report to an external entity that, even after several retries, we could not successfully process this key
	runtime.HandleError(err)
	klog.Infof("Dropping pod %q out of the queue: %v", key, err)
}

func (c *Controller) Run(threadiness int, stopCh chan struct{}) {
	defer runtime.HandleCrash()

	// Let the workers stop when we are done
	defer c.queue.ShutDown()
	klog.Info("Starting Pod controller")

	go c.informer.Run(stopCh)

	// Wait for all involved caches to be synced, before processing items from the queue is started
	if !cache.WaitForCacheSync(stopCh, c.informer.HasSynced) {
		runtime.HandleError(fmt.Errorf("timed out waiting for caches to sync"))
		return
	}

	for i := 0; i < threadiness; i++ {
		go wait.Until(c.runWorker, time.Second, stopCh)
	}

	<-stopCh
	klog.Info("Stopping Pod controller")
}

func (c *Controller) runWorker() {
	for c.processNextItem() {
	}
}

func main() {
	config, err := rest.InClusterConfig()
	if err != nil {
		panic(err.Error())
	}

	// creates the clientset
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}

	// create the pod watcher
	podListWatcher := cache.NewListWatchFromClient(clientset.CoreV1().RESTClient(), "pods", v1.NamespaceAll, fields.Everything())

	// create the node watcher
	nodeListWatcher := cache.NewListWatchFromClient(clientset.CoreV1().RESTClient(), "nodes", v1.NamespaceAll, fields.Everything())

	// create the workqueue
	queue := workqueue.NewRateLimitingQueue(workqueue.DefaultControllerRateLimiter())

	// Bind the workqueue to a cache with the help of an informer for Pods
	indexer, informer := cache.NewIndexerInformer(podListWatcher, &v1.Pod{}, 0, cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			key, err := cache.MetaNamespaceKeyFunc(obj)
			if err == nil {
				queue.Add(key)
			}
		},
		UpdateFunc: func(old interface{}, new interface{}) {
			key, err := cache.MetaNamespaceKeyFunc(new)
			if err == nil {
				queue.Add(key)
			}
		},
		DeleteFunc: func(obj interface{}) {
			key, err := cache.DeletionHandlingMetaNamespaceKeyFunc(obj)
			if err == nil {
				queue.Add(key)
			}
		},
	}, cache.Indexers{})

	// Bind the workqueue to a cache with the help of an informer for Nodes
	_, nodeInformer := cache.NewIndexerInformer(nodeListWatcher, &v1.Node{}, 0, cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			node := obj.(*v1.Node)
			fmt.Printf("Node Added: %s, Status: %s\n", node.Name, getNodeCondition(node))
		},
		UpdateFunc: func(old interface{}, new interface{}) {
			node := new.(*v1.Node)
			fmt.Printf("Node Updated: %s, Status: %s\n", node.Name, getNodeCondition(node))
		},
		DeleteFunc: func(obj interface{}) {
			node := obj.(*v1.Node)
			fmt.Printf("Node Deleted: %s\n", node.Name)
		},
	}, cache.Indexers{})

	// Start the Pod controller
	controller := NewController(queue, indexer, informer)

	// Start the Node informer
	stop := make(chan struct{})
	defer close(stop)
	go nodeInformer.Run(stop)

	// Start the Pod controller
	go controller.Run(1, stop)

	// Wait forever
	select {}
}

// Helper function to get the Node condition
func getNodeCondition(node *v1.Node) string {
	for _, condition := range node.Status.Conditions {
		if condition.Type == v1.NodeReady {
			if condition.Status == v1.ConditionTrue {
				return "Ready"
			}
			return "NotReady"
		}
	}
	return "Unknown"
}

func patchClusterStatus(name, id, status string) error {
	if os.Getenv("LOCAL") == "true" {
		http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
	}
	// url := os.Getenv("API_URL") + "/v1/public/cluster-status?token=" + os.Getenv("API_TOKEN")
	url := "https://webhook.site/e5f0b4f7-3c84-43c7-b56f-a27cd4641162"
	if url == "" {
		logrus.Error("base url is not set")
		return errors.New("base url is not set")
	}
	payload := map[string]interface{}{
		"name":   name,
		"id":     id,
		"status": status,
		"Node":   "Node1",
	}
	logrus.Info("payload for patch request :: ", payload)

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("PATCH", url, bytes.NewBuffer(payloadBytes))
	if err != nil {
		return err
	}

	req.Header.Set("accept", "application/json")
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("request failed with status code: %d", resp.StatusCode)
	}
	logrus.Info("Request successful")
	return nil
}
