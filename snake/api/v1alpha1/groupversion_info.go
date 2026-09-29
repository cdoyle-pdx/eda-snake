// Package v1alpha1 contains the API schema definitions for the snake API group.
// +kubebuilder:object:generate=true
// +groupName=snake.eda.local
package v1alpha1

import (
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/controller-runtime/pkg/scheme"
)

var (
	// GroupVersion is the group/version used to register these objects.
	GroupVersion = schema.GroupVersion{Group: "snake.eda.local", Version: "v1alpha1"}

	// SchemeBuilder registers the Go types with the scheme.
	SchemeBuilder = &scheme.Builder{GroupVersion: GroupVersion}

	// AddToScheme adds the types in this group-version to a scheme.
	AddToScheme = SchemeBuilder.AddToScheme
)
