/*
Copyright 2026.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime/schema"
)

var KSnakeScoreGVK = schema.GroupVersionKind{Group: "eda.cdoyle.dev", Version: "v1alpha1", Kind: "SnakeScore"}

// SnakeScore is the Schema for the snakescores API
// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:path=snakescores,scope=Namespaced
type SnakeScore struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   SnakeScoreSpec   `json:"spec,omitempty"`
	Status SnakeScoreStatus `json:"status,omitempty"`
}

// SnakeScoreList contains a list of SnakeScore
// +kubebuilder:object:root=true
type SnakeScoreList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []SnakeScore `json:"items"`
}

func init() {
	SchemeBuilder.Register(&SnakeScore{}, &SnakeScoreList{})
}
