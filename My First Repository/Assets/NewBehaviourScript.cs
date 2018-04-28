using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class NewBehaviourScript : MonoBehaviour {

	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		transform.Rotate (10000000000000000 * Time.deltaTime, 100000000000 * Time.deltaTime, 100000000000000000 * Time.deltaTime);
	}
}
