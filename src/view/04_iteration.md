# การวนซ้ำ

ไม่ว่าคุณจะกำลังทำรายการสิ่งที่ต้องทำ (to-do list), ตารางข้อมูล หรือแกลเลอรีรูปภาพสินค้า การวนลูปแสดงรายการข้อมูล (iteration) ก็นับเป็นงานพื้นฐานที่พบได้ตลอดเวลาในเว็บแอปพลิเคชัน และการตรวจจับความเปลี่ยนแปลง (reconciliation) ระหว่างรายการข้อมูลชุดเดิมกับชุดใหม่ก็เป็นหนึ่งในงานที่ท้าทายที่สุดสำหรับเฟรมเวิร์กเช่นกัน

Leptos มีสองรูปแบบหลักในการจัดการกับการวนลูปแสดงรายการข้อมูล:

1. สำหรับวิวแบบสแตติก: `Vec<_>`
2. สำหรับรายการแบบไดนามิก: `<For/>`

## วิวแบบสแตติกด้วย `Vec<_>`

ในบางครั้ง คุณอาจต้องการแสดงผลไอเท็มหลายชิ้นซ้ำ ๆ โดยที่รายการข้อมูลต้นทางไม่ได้มีการเปลี่ยนแปลง ในกรณีนี้ สิ่งสำคัญที่ควรรู้คือ คุณสามารถแทรก `Vec<IV> where IV: IntoView` ใด ๆ ลงในวิวได้โดยตรง พูดง่าย ๆ ก็คือ ถ้าคุณเรนเดอร์ค่า `T` ได้ คุณก็สามารถเรนเดอร์ `Vec<T>` ได้ด้วยเช่นกัน

```rust
let values = vec![0, 1, 2];
view! {
    // this will just render "012"
    <p>{values.clone()}</p>
    // or we can wrap them in <li>
    <ul>
        {values.into_iter()
            .map(|n| view! { <li>{n}</li>})
            .collect::<Vec<_>>()}
    </ul>
}
```

Leptos ยังมีฟังก์ชันตัวช่วย `.collect_view()` ที่ให้คุณรวบรวมอิเทอเรเตอร์ใด ๆ ของ `T: IntoView` ให้กลายเป็น `Vec<View>` ได้สะดวกรวดเร็ว:

```rust
let values = vec![0, 1, 2];
view! {
    // this will just render "012"
    <p>{values.clone()}</p>
    // or we can wrap them in <li>
    <ul>
        {values.into_iter()
            .map(|n| view! { <li>{n}</li>})
            .collect_view()}
    </ul>
}
```

การที่ *ตัวรายการ* เป็นแบบสแตติก ไม่ได้แปลว่าอินเทอร์เฟซจะต้องเป็นแบบคงที่เสมอไป คุณยังสามารถเรนเดอร์ไอเท็มที่มีความไดนามิกรีแอกทีฟอยู่ภายในรายการแบบสแตติกได้

```rust
// create a list of 5 signals
let length = 5;
let counters = (1..=length).map(|idx| RwSignal::new(idx));
```

สังเกตว่าในตัวอย่างนี้ แทนที่เราจะเรียก `signal()` ซึ่งจะได้ทูเพิลแยกตัวอ่านกับตัวเขียน เราเลือกใช้ `RwSignal::new()` เพื่อให้ได้สัญญาณที่สามารถอ่านและเขียนได้ในตัวเดียว ซึ่งสะดวกกว่ามากในสถานการณ์ที่เราไม่อยากคอยส่งทูเพิลไปมา

```rust
// each item manages a reactive view
// but the list itself will never change
let counter_buttons = counters
    .map(|count| {
        view! {
            <li>
                <button
                    on:click=move |_| *count.write() += 1
                >
                    {count}
                </button>
            </li>
        }
    })
    .collect_view();

view! {
    <ul>{counter_buttons}</ul>
}
```

คุณ *สามารถ* เรนเดอร์ `Fn() -> Vec<_>` แบบรีแอกทีฟได้เช่นกัน แต่พึงระวังว่านี่คือการอัปเดตรายการแบบ “ไม่มีคีย์” (unkeyed) โดยเฟรมเวิร์กจะนำเอลิเมนต์ DOM เดิมที่มีอยู่กลับมาใช้ซ้ำ แล้วอัปเดตค่าใหม่ตามลำดับตำแหน่งใน `Vec<_>` ชุดใหม่ ซึ่งหากคุณทำแค่การเพิ่มหรือลบไอเท็มที่ส่วนท้ายสุดของรายการ วิธีนี้ก็ทำงานได้ดี แต่ถ้ามีการสลับตำแหน่งไอเท็ม หรือแทรกไอเท็มใหม่เข้ามาตรงกลาง วิธีนี้จะบีบให้เบราว์เซอร์ต้องทำงานซ้ำซ้อนมากเกินจำเป็น และอาจทำให้สถานะของช่องอินพุต (input state) หรือแอนิเมชัน CSS เพี้ยนไปอย่างคาดไม่ถึง (อ่านรายละเอียดเปรียบเทียบระหว่างแบบ "มีคีย์" (keyed) กับ "ไม่มีคีย์" (unkeyed) เพิ่มเติมพร้อมตัวอย่างจริงได้จาก [บทความนี้](https://www.stefankrause.net/wp/?p=342))

โชคดีที่ Leptos มีวิธีจัดการกับการวนลูปรายการแบบมีคีย์ได้อย่างมีประสิทธิภาพสูง

## การเรนเดอร์แบบไดนามิกด้วยคอมโพเนนต์ `<For/>`

คอมโพเนนต์ [`<For/>`](https://docs.rs/leptos/latest/leptos/control_flow/fn.For.html) ออกแบบมาสำหรับการแสดงรายการไดนามิกแบบมีคีย์ โดยรับพร็อพสำคัญ 3 ตัว:

- `each`: ฟังก์ชันรีแอกทีฟที่คืนค่าไอเท็ม `T` ที่จะถูกวนซ้ำ
- `key`: ฟังก์ชันคีย์ที่รับ `&T` แล้วคืนค่าคีย์หรือ ID ที่เสถียรและไม่ซ้ำกัน
- `children` (ลูก): เรนเดอร์แต่ละ `T` ให้เป็นวิว

`key` มีความสำคัญอย่างยิ่ง: คุณสามารถเพิ่ม ลบ และย้ายไอเท็มภายในรายการได้อย่างอิสระ ตราบใดที่คีย์ของแต่ละไอเท็มคงที่ตลอดเวลา เฟรมเวิร์กก็ไม่จำเป็นต้องเรนเดอร์ไอเท็มนั้นใหม่ นอกเสียจากไอเท็มที่เพิ่งเพิ่มเข้ามาใหม่เท่านั้น และยังสามารถย้ายหรือลบเอลิเมนต์ใน DOM ได้อย่างมีประสิทธิภาพสูง ทำให้การอัปเดตรายการทำงานได้เร็วที่สุดโดยใช้ทรัพยากรน้อยที่สุด

การกำหนด `key` ที่ดีอาจต้องใส่ใจสักนิด โดยทั่วไปคุณ *ไม่* ควรใช้ดัชนี (index) เป็นคีย์ เพราะมันไม่เสถียร—หากมีการลบหรือย้ายตำแหน่งไอเท็ม ดัชนีของไอเท็มเหล่านั้นก็จะเปลี่ยนตามไปด้วย

แนวทางที่ดีมากคือการสร้าง ID ที่ไม่ซ้ำกันให้กับแต่ละแถวตั้งแต่ตอนที่สร้างข้อมูลขึ้นมา แล้วนำ ID นั้นมาใช้เป็นคีย์ในฟังก์ชัน key

ลองศึกษาการทำงานจริงได้จากตัวอย่างคอมโพเนนต์ `<DynamicList/>` ด้านล่างนี้:

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/4-iteration-0-7-dw4dfl?file=%2Fsrc%2Fmain.rs%3A1%2C1-159%2C1&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/4-iteration-0-7-dw4dfl?file=%2Fsrc%2Fmain.rs%3A1%2C1-159%2C1&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

// Iteration is a very common task in most applications.
// So how do you take a list of data and render it in the DOM?
// This example will show you the two ways:
// 1) for mostly-static lists, using Rust iterators
// 2) for lists that grow, shrink, or move items, using <For/>

#[component]
fn App() -> impl IntoView {
    view! {
        <h1>"Iteration"</h1>
        <h2>"Static List"</h2>
        <p>"Use this pattern if the list itself is static."</p>
        <StaticList length=5/>
        <h2>"Dynamic List"</h2>
        <p>"Use this pattern if the rows in your list will change."</p>
        <DynamicList initial_length=5/>
    }
}

/// A list of counters, without the ability
/// to add or remove any.
#[component]
fn StaticList(
    /// How many counters to include in this list.
    length: usize,
) -> impl IntoView {
    // create counter signals that start at incrementing numbers
    let counters = (1..=length).map(|idx| RwSignal::new(idx));

    // when you have a list that doesn't change, you can
    // manipulate it using ordinary Rust iterators
    // and collect it into a Vec<_> to insert it into the DOM
    let counter_buttons = counters
        .map(|count| {
            view! {
                <li>
                    <button
                        on:click=move |_| *count.write() += 1
                    >
                        {count}
                    </button>
                </li>
            }
        })
        .collect::<Vec<_>>();

    // Note that if `counter_buttons` were a reactive list
    // and its value changed, this would be very inefficient:
    // it would rerender every row every time the list changed.
    view! {
        <ul>{counter_buttons}</ul>
    }
}

/// A list of counters that allows you to add or
/// remove counters.
#[component]
fn DynamicList(
    /// The number of counters to begin with.
    initial_length: usize,
) -> impl IntoView {
    // This dynamic list will use the <For/> component.
    // <For/> is a keyed list. This means that each row
    // has a defined key. If the key does not change, the row
    // will not be re-rendered. When the list changes, only
    // the minimum number of changes will be made to the DOM.

    // `next_counter_id` will let us generate unique IDs
    // we do this by simply incrementing the ID by one
    // each time we create a counter
    let mut next_counter_id = initial_length;

    // we generate an initial list as in <StaticList/>
    // but this time we include the ID along with the signal
    // see NOTE in add_counter below re: ArcRwSignal
    let initial_counters = (0..initial_length)
        .map(|id| (id, ArcRwSignal::new(id + 1)))
        .collect::<Vec<_>>();

    // now we store that initial list in a signal
    // this way, we'll be able to modify the list over time,
    // adding and removing counters, and it will change reactively
    let (counters, set_counters) = signal(initial_counters);

    let add_counter = move |_| {
        // create a signal for the new counter
        // we use ArcRwSignal here, instead of RwSignal
        // ArcRwSignal is a reference-counted type, rather than the arena-allocated
        // signal types we've been using so far.
        // When we're creating a collection of signals like this, using ArcRwSignal
        // allows each signal to be deallocated when its row is removed.
        let sig = ArcRwSignal::new(next_counter_id + 1);
        // add this counter to the list of counters
        set_counters.update(move |counters| {
            // since `.update()` gives us `&mut T`
            // we can just use normal Vec methods like `push`
            counters.push((next_counter_id, sig))
        });
        // increment the ID so it's always unique
        next_counter_id += 1;
    };

    view! {
        <div>
            <button on:click=add_counter>
                "Add Counter"
            </button>
            <ul>
                // The <For/> component is central here
                // This allows for efficient, key list rendering
                <For
                    // `each` takes any function that returns an iterator
                    // this should usually be a signal or derived signal
                    // if it's not reactive, just render a Vec<_> instead of <For/>
                    each=move || counters.get()
                    // the key should be unique and stable for each row
                    // using an index is usually a bad idea, unless your list
                    // can only grow, because moving items around inside the list
                    // means their indices will change and they will all rerender
                    key=|counter| counter.0
                    // `children` receives each item from your `each` iterator
                    // and returns a view
                    children=move |(id, count)| {
                        // we can convert our ArcRwSignal to a Copy-able RwSignal
                        // for nicer DX when moving it into the view
                        let count = RwSignal::from(count);
                        view! {
                            <li>
                                <button
                                    on:click=move |_| *count.write() += 1
                                >
                                    {count}
                                </button>
                                <button
                                    on:click=move |_| {
                                        set_counters
                                            .write()
                                            .retain(|(counter_id, _)| {
                                                counter_id != &id
                                            });
                                    }
                                >
                                    "Remove"
                                </button>
                            </li>
                        }
                    }
                />
            </ul>
        </div>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>

### การเข้าถึงอินเด็กซ์ระหว่างการวนซ้ำด้วย `<ForEnumerate/>`

ในกรณีที่คุณต้องการเข้าถึงดัชนี (index) ของไอเท็มแบบเรียลไทม์ระหว่างการวนลูป Leptos ได้เตรียมคอมโพเนนต์ [`<ForEnumerate/>`](https://docs.rs/leptos/latest/leptos/control_flow/fn.ForEnumerate.html) ไว้ให้ใช้งาน

คอมโพเนนต์นี้รับพร็อพเหมือนกับ [`<For/>`](https://docs.rs/leptos/latest/leptos/control_flow/fn.For.html) ทุกประการ แต่เมื่อเรนเดอร์ `children` มันจะส่งพารามิเตอร์ `ReadSignal<usize>` ที่เป็นดัชนีแบบรีแอกทีฟมาให้ด้วย:

```rust
#[derive(Copy, Clone, Debug, PartialEq, Eq)]
struct Counter {
  id: usize,
  count: RwSignal<i32>
}

<ForEnumerate
    each=move || counters.get() // Same as <For/>
    key=|counter| counter.id    // Same as <For/>
    // Provides the index as a signal and the child T
    children={move |index: ReadSignal<usize>, counter: Counter| {
        view! {
            <button>{move || index.get()} ". Value: " {move || counter.count.get()}</button>
        }
    }}
/>
```

หรือจะใช้ร่วมกับไวยากรณ์ `let` ที่กระชับและสะดวกกว่าก็ได้เช่นกัน:
```rust
<ForEnumerate
    each=move || counters.get() // Same as <For/>
    key=|counter| counter.id    // Same as <For/>
    let(idx, counter)           // let syntax
>
    <button>{move || idx.get()} ". Value: " {move || counter.count.get()}</button>
</ ForEnumerate>
```
